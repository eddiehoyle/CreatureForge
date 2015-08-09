#!/usr/bin/env python

"""
"""

from collections import OrderedDict

from maya import cmds

from creatureforge.lib import libname
from creatureforge.lib import libattr
from creatureforge.lib import libconstraint
from creatureforge.model.base import Module
from creatureforge.exceptions import DuplicateNameError

AXIS = ["X", "Y", "Z"]

class Guide(Module):

    RADIUS = 1.0
    SUFFIX = "gde"

    ORIENT = OrderedDict([("xyz", [(0, 0, 0), (0, 180, 0)]),
                          ("xzy", [(-90, 0, 0), (-90, 180, 0)]),
                          ("yxz", [(0, -180, -90), (0, 0, 90)]),
                          ("yzx", [(0, -90, -90), (180, 90, -90)]),
                          ("zxy", [(-90, 180, -90), (90, 180, -90)]),
                          ("zyx", [(-90, 90, -90), (-90, -90, 90)])])

    DEFAULT = ["world", "custom"]

    def __init__(self, position, description, index=0):
        super(Guide, self).__init__(position, description, index)

        self.__constraints = {}

    @property
    def aim(self):
        return self._dag.get("aim")

    @property
    def up(self):
        return self._dag.get("up")

    @property
    def setup(self):
        return self._dag.get("setup")

    @property
    def shapes(self):
        return self._dag.get("shapes")

    @property
    def constraint(self):
        return self._nondag.get("constraint")

    def __create_setup(self):
        name = libname.rename(self.node, suffix="setup")
        setup = cmds.createNode("transform", name=name)
        cmds.pointConstraint(self.node, setup, mo=False)
        self.store("setup", setup)

    def __create_node(self):

        # Create joint
        cmds.select(cl=True)
        cmds.joint(name=self.node)
        libattr.set(self.node, "radius", channelBox=False, l=True)
        cmds.select(cl=True)
        libattr.set(self.node, "drawStyle", 2)

        # Create shapes
        transform = cmds.sphere(radius=Guide.RADIUS, ch=False)[0]
        shape = cmds.listRelatives(transform, type="nurbsSurface", children=True)[0]
        shape = cmds.rename(shape, libname.rename(self.node, shape=True))
        cmds.parent(shape, self.node, r=True, s=True)
        cmds.delete(transform)

        self.store("shapes", shape, append=True)

        # Add attributes
        libattr.add_double(self.node, "guideScale", min=0.01, dv=1)
        libattr.add_enum(self.node, "guideAimOrient", enums=Guide.ORIENT.keys())
        libattr.add_bool(self.node, "guideAimFlip")
        libattr.add_enum(self.node, "guideAimAt", enums=Guide.DEFAULT)

        libattr.add_double(self.node, "guideOffsetOrientX")
        libattr.add_double(self.node, "guideOffsetOrientY")
        libattr.add_double(self.node, "guideOffsetOrientZ")

        for attr in ["guideScale", "guideAimOrient", "guideAimFlip", "guideAimAt"]:
            libattr.set(self.node, attr, keyable=False, channelBox=True)

    def __create_aim(self):
        name = libname.rename(self.node, suffix="aim")
        aim = cmds.createNode("transform", name=name)
        libattr.set(aim, "translateZ", -0.00000001)
        cmds.parent(aim, self.setup)
        self.store("aim", aim)

    def __create_up(self):
        up = Up(self)
        up.create()
        self.store("up", up)
        cmds.parent(up.grp, self.setup)

    def __create_scale(self):
        cl, cl_handle = cmds.cluster(self.shapes)
        libattr.set(cl, "relative", True)
        cl_handle = cmds.rename(cl_handle, libname.rename(self.node, append="scale", suffix="clh"))
        self.store("scale", cl_handle)

        for axis in AXIS:
            cmds.connectAttr("{node}.guideScale".format(node=self.node),
                             "{handle}.scale{axis}".format(handle=cl_handle, axis=axis))

        cmds.parent(cl_handle, self.setup)

    def __setup_network(self):

        # Create main aim constraint
        constraint = cmds.aimConstraint(self.node,
                                        self.aim,
                                        worldUpObject=self.up.node,
                                        offset=(0, 0, 0),
                                        aimVector=(1, 0, 0),
                                        upVector=(0, 1, 0),
                                        worldUpType='object')[0]

        self.__constraints["aim"] = libconstraint.get_handler(constraint)

        # Create custom aim constraint offsets
        offset_pma = cmds.createNode("plusMinusAverage",
                                     name=libname.rename(self.node, suffix="pma", append="custom"))

        cmds.connectAttr("{pma}.output3D".format(pma=offset_pma),
                         "{constraint}.offset".format(constraint=constraint))

        for pair_index, axises in enumerate(Guide.ORIENT):

            primary, secondary = self.ORIENT[axises]

            # Axis condition
            pair_cond = cmds.createNode("condition", name=libname.rename(self.node, append="aim%s" % pair_index, suffix="cond"))

            cmds.connectAttr("%s.guideAimOrient" % self.node, "%s.firstTerm" % pair_cond)
            cmds.connectAttr("%s.outColor" % pair_cond, "%s.input3D[%s]" % (offset_pma, pair_index))

            libattr.set(pair_cond, "secondTerm", pair_index)
            libattr.set(pair_cond, "colorIfFalse", *(0, 0, 0), type="float3")

            # Flip condition
            flip_cond = cmds.createNode("condition", name=libname.rename(self.node, append="aim%sFlip" % pair_index, suffix="cond"))
            cmds.connectAttr("%s.guideAimFlip" % self.node, "%s.firstTerm" % flip_cond)
            cmds.connectAttr("%s.outColor" % flip_cond, "%s.colorIfTrue" % pair_cond)

            libattr.set(flip_cond, "secondTerm", 1)
            libattr.set(flip_cond, "colorIfTrue", *secondary, type="float3")
            libattr.set(flip_cond, "colorIfFalse", *primary, type="float3")

        # Add custom orient offset
        for attr, axis in zip(["guideOffsetOrientX", "guideOffsetOrientY", "guideOffsetOrientZ"], ["x", "y", "z"]):
            cmds.connectAttr("%s.%s" % (self.node, attr),
                             "%s.input3D[%s].input3D%s" % (offset_pma,
                                                           (pair_index + 1),
                                                           axis))

        self.store("constraint", constraint, dag=False)

    def _create(self):

        if self.exists:
            err = "Cannot create node as it already exists: {node}".format(node=self.node)
            raise DuplicateNameError(err)

        self.__create_node()
        self.__create_setup()
        self.__create_aim()
        self.__create_up()
        self.__create_scale()

        self.__setup_network()


class Up(Module):

    SUFFIX = "up"
    RAIDUS = 0.3

    def __init__(self, guide):

        self.__guide = guide

        super(Up, self).__init__(*guide.tokens)

    @property
    def guide(self):
        return self.__guide

    @property
    def grp(self):
        return self._dag.get("grp")

    @property
    def shapes(self):
        return self._dag.get("shapes")

    def __create_node(self):
        grp_name = libname.rename(self.node, append="Up", suffix="grp")
        grp = cmds.createNode("transform", name=grp_name)
        self.store("grp", grp)

        sphere = cmds.sphere(name=self.node, radius=Up.RAIDUS)[0]
        shapes = cmds.listRelatives(sphere, shapes=True)

        cmds.parent(sphere, grp)

        # Add attributes
        libattr.add_double(self.node, "guideScale", min=0.01, dv=1)

        for attr in ["guideScale"]:
            libattr.set(self.node, attr, keyable=False, channelBox=True)

        for axis in AXIS:
            cmds.connectAttr("{node}.guideScale".format(node=self.guide.node),
                             "{grp}.scale{axis}".format(grp=grp, axis=axis))

        self.store("node", sphere)
        self.store("shapes", shapes, append=shapes)

    def __create_scale(self):
        cl, cl_handle = cmds.cluster(self.shapes)
        libattr.set(cl, "relative", True)
        cl_handle = cmds.rename(cl_handle, libname.rename(self.node, append="upScale", suffix="clh"))
        self.store("scale", cl_handle)

        for axis in AXIS:
            cmds.connectAttr("{node}.guideScale".format(node=self.node),
                             "{handle}.scale{axis}".format(handle=cl_handle, axis=axis))

        cmds.parent(cl_handle, self.grp)

    def _create(self):
        self.__create_node()
        self.__create_scale()

        libattr.set(self.node, "translateY", 3)


class Tendon(Module):

    SUFFIX = "cncShape"

    def __init__(self, child, parent):

        self.__child = child
        self.__parent = parent

        super(Tendon, self).__init__(*child.tokens)

    @property
    def child(self):
        return self.__child

    @property
    def parent(self):
        return self.__parent

    def __create_annotation(self):
        shape = cmds.createNode("annotationShape", name=self.node)
        transform = cmds.listRelatives(shape, parent=True)[0]

        cmds.parent(self.node, self.parent.node, shape=True, relative=True)
        cmds.delete(transform)

        libattr.set(self.node, "overrideEnabled", True)
        libattr.set(self.node, "overrideColor", 18)
        libattr.set(self.node, "displayArrow", False)
        libattr.set(self.node, "displayArrow", True)
        cmds.connectAttr("{src}.worldMatrix[0]".format(src=self.child.shapes[0]),
                         "{dst}.dagObjectMatrix[0]".format(dst=self.node),
                         force=True)

    def _create(self):
        self.__create_annotation()
