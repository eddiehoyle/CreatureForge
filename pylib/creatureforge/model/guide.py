#!/usr/bin/env python

"""
"""

import time
import logging
from collections import OrderedDict

from maya import cmds

from creatureforge.lib import libname
from creatureforge.lib import libattr
from creatureforge.lib import libutil
from creatureforge.lib import libconstraint
from creatureforge.decorators import Memoized
from creatureforge.model.base import Module
from creatureforge.exceptions import DuplicateNameError
from creatureforge.exceptions import GuideDoesNotExistError
from creatureforge.exceptions import GuideHierarchyError

class GuideError(Exception):
    pass

logger = logging.getLogger(__name__)

AXIS = ["X", "Y", "Z"]


def cache(func):
    def wraps(*args, **kwargs):
        node = args[0].node
        if not cmds.objExists(node):
            err = "Guide does not exist: '{node}'".format(node=node)
            raise RuntimeError(err)
        return func(*args, **kwargs)
    return wraps


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

    @classmethod
    def validate(cls, node):
        try:
            if not str(node).endswith(cls.SUFFIX):
                raise NameError()
            if isinstance(node, cls):
                return node
            else:
                return Guide(*libname.tokens(str(node))).reinit()
        except Exception:
            msg = "'{node}' is not a valid guide.".format(node=node)
            logger.error(msg)
            raise TypeError(msg)

    def __init__(self, position, description, index=0):
        super(Guide, self).__init__(position, description, index)

    def reinit(self):
        super(Guide, self).reinit()
        self.store("up", Up(self))
        return self

    @cache
    def get_tendons(self):
        return tuple(map(lambda g: Tendon(g, self), self.children))

    @cache
    def get_aim(self):
        return self._dag.get("aim")

    @cache
    def get_up(self):
        return Up(self)

    @cache
    def get_setup(self):
        return self._dag.get("setup")

    @cache
    def get_shapes(self):
        return self._dag.get("shapes", tuple())

    @cache
    def get_constraint(self):
        return self._nondag.get("aim_constraint")

    @cache
    def get_condition(self):
        return self._nondag.get("aim_condition")

    @cache
    def get_parent(self):
        parent = cmds.listRelatives(self.get_node(), parent=True, type="joint")
        if parent:
            return Guide.validate(parent[0])
        return None

    @cache
    def get_children(self):
        children = cmds.listRelatives(
            self.get_node(), children=True, type="joint") or tuple()
        return tuple(map(Guide.validate, children))

    @cache
    def get_snapshot(self):
        parent = self.get_parent()
        return dict(node=self.get_node(),
                    parent=self.get_parent().get_node(),
                    children=self.get_children(),
                    offset_orient=self.get_offset_orient(),
                    aim_orient=self.get_aim_orient(),
                    aim_at=self.get_aim_at(),
                    aim_flip=bool(cmds.getAttr("%s.guideAimFlip" % self.get_node())),
                    position=self.get_position(worldspace=True),
                    up_position=self.get_up().get_position(worldspace=True))

    @cache
    def compile(self):

        cmds.select(cl=True)

        # Get some joint creation args
        aim = self.get_aim()
        orientation = cmds.xform(aim, q=1, ws=1, ro=1)
        rotation_order = Guide.ORIENT.keys()[cmds.getAttr("%s.guideAimOrient" % self.get_node())]

        # Create joint
        joint = cmds.joint(name=libname.rename(self.get_name().compile(), suffix="jnt"),
                           orientation=orientation,
                           position=self.get_position(worldspace=True),
                           rotationOrder=rotation_order)

        cmds.select(cl=True)

        msg = "Compiled '{node}'.".format(node=self.get_node())
        logger.info(msg)

        return joint

    @cache
    def get_aim_at(self):
        enums = cmds.attributeQuery("guideAimAt", node=self.get_node(), listEnum=True)[0].split(":")
        target = enums[cmds.getAttr("{node}.guideAimAt".format(node=self.get_node()))]

        # Create guide object if valid
        if target not in self.DEFAULT:
            return Guide(*libname.tokens(target))

        return None

    @cache
    def get_aim_orient(self):
        order = Guide.ORIENT.keys()
        orient = order[cmds.getAttr("{node}.guideAimOrient".format(
            node=self.get_node()))]
        return tuple(orient)

    @cache
    def get_offset_orient(self):
        paths = []
        for axis in AXIS:
            paths.append("{node}.guideOffsetOrient{axis}".format(
                node=self.get_node(), axis=axis))
        return tuple(map(cmds.getAttr, paths))

    @cache
    def get_translates(self, worldspace=True):
        return tuple(cmds.xform(self.get_node(), q=True, ws=worldspace, t=True))

    @cache
    def set_translates(self, x, y, z, worldspace=False):
        logger.debug("Setting {node} position: ({x}, {y}, {z})".format(
            node=self.get_node(), x=x, y=y, z=z))
        cmds.xform(self.get_node(), ws=worldspace, t=[x, y, z])

    @cache
    def copy(self):
        name = libname.generate(self.get_node())
        guide = Guide(*libname.tokens(name))
        guide.create()
        return guide

    @cache
    def has_parent(self, guide):
        parent = self.get_parent()
        while parent:
            if guide.node == parent.node:
                return True
            parent = parent.get_parent()
        return parent

    @cache
    def has_child(self, guide):
        return guide in self.children

    @cache
    def set_parent(self, guide):

        t = time.time()

        # Try to parent to itself
        if self == guide:
            err = "Cannot parent '{node}' to itself.".format(node=self.get_node())
            raise GuideError(err)

        # Is guide already parent
        parent = self.get_parent()
        if parent == guide:
            err = "'{guide}' is already a parent of '{node}'".format(
                guide=guide, node=self.get_node())
            return parent

        # Is guide below self in hierarchy
        if guide.has_parent(self):
            guide.remove_parent()

        # If a parent already exists
        if parent:
            self.remove_parent()

        guide.__add_aim(self)
        msg = ("Set parent: '{guide}' -> '{node}' "
               "({time:0.3f}s)").format(guide=guide,
                                        node=self.get_node(),
                                        time=(time.time() - t))
        logger.info(msg)

        return guide

    @cache
    def add_child(self, guide):

        t = time.time()

        # Try to parent to itself
        if self.get_node() == guide.node:
            err = "Cannot add '{node}' to itself as child.".format(
                node=self.get_node())
            raise GuideError(err)

        # Guide is already a child of self
        if self.has_child(guide):
            err = "'{guide}' is already a child of '{node}'.".format(
                guide=guide, node=self.get_node())
            logger.warn(err)
            return self.children.index(guide.node)

        # If guide has any parent already
        if guide.parent:
            guide.remove_parent()

        # Is guide above self in hierarchy
        if self.has_parent(guide):
            self.remove_parent()

        self.__add_aim(guide)
        msg = ("Added child '{node}' <- '{guide}' "
               "({time:0.3f}s)").format(guide=guide,
                                        node=self.get_node(),
                                        time=(time.time() - t))
        logger.info(msg)

        return guide

    @cache
    def remove(self):
        self.remove_parent()
        for child in self.get_children():
            self.remove_child(child)
        self.get_up().remove()
        super(Guide, self).remove()
        logger.info("Removed '{node}'".format(node=self.get_name().compile()))

    @cache
    def remove_parent(self):
        parent = self.get_parent()
        if parent:
            parent.remove_child(self)

    @cache
    def remove_child(self, guide):
        self.__remove_aim(guide)

    def __add_aim(self, guide):
        """
        Private aim creation method. Add the input guide as a child
        by extending this guides aimConstraint values and adding
        an aim enum value to the 'aimAt' attribute.
        """

        aim_constraint = self.get_aim()
        cmds.aimConstraint(guide.aim, aim_constraint,
                           worldUpObject=self.get_up().node,
                           worldUpType="object",
                           aimVector=(1, 0, 0),
                           upVector=(0, 1, 0),
                           mo=False)

        # Edit aim attribute on node to include new child
        enums = cmds.attributeQuery("guideAimAt", node=self.get_node(), listEnum=True)[0].split(":")
        enums.append(guide.node)
        libattr.edit_enum(self.get_node(), "guideAimAt", enums=enums)

        # Create connector
        con = Tendon(guide, self)
        con.create()

        # Parent new guide under self
        cmds.parent(guide.node, self.get_node(), a=True)

        return guide

    def __remove_aim(self, guide):

        t = time.time()

        if guide not in self.children:
            error = "'{child}' is not a child of '{parent}'.".format(
                child=guide, parent=self)
            raise GuideHierarchyError(error)

        # Remove connector
        tendons = self.get_tendons()
        for con in tendons:
            if con.parent == self:
                con.remove()
                break

        # Parent guide to world
        cmds.parent(guide.node, world=True)

        # Remove enum name
        enums = cmds.attributeQuery("guideAimAt", node=self.get_node(), listEnum=True)[0].split(":")
        enums.remove(guide.node)
        libattr.edit_enum(self.get_node(), "guideAimAt", enums)
        libattr.set(self.get_node(), "guideAimAt", len(enums) - 1)

        aim_constraint = self.get_constraint()
        aliases = cmds.aimConstraint(aim_constraint, q=True, wal=True)
        for alias in aliases:
            if not cmds.listConnections("%s.%s" % (aim_constraint, alias),
                                        source=True,
                                        destination=False,
                                        plugs=True):
                libattr.set(aim_constraint, alias, 0)

        # Default to world if no aim objects are attached
        if len(enums) == len(Guide.DEFAULT):
            libattr.set(self.get_node(), "guideAimAt", 0)

        logger.debug("'%s' remove child: '%s' (%0.3fs)" % (self.get_node(),
                                                           guide.node,
                                                           time.time() - t))

    def __create_setup(self):
        name = libname.rename(self.get_node(), suffix="setup")
        setup = cmds.createNode("transform", name=name)
        cmds.pointConstraint(self.get_node(), setup, mo=False)
        self.store("setup", setup)

    def __create_node(self):

        # Create joint
        cmds.select(cl=True)
        cmds.joint(name=self.get_name().compile())
        libattr.set(self.get_node(), "radius", channelBox=False, l=True)
        cmds.select(cl=True)
        libattr.set(self.get_node(), "drawStyle", 2)

        # Create shapes
        transform = cmds.sphere(radius=Guide.RADIUS, ch=False)[0]
        shape = cmds.listRelatives(transform, type="nurbsSurface", children=True)[0]
        shape = cmds.rename(shape, libname.rename(self.get_node(), shape=True))
        cmds.parent(shape, self.get_node(), r=True, s=True)
        cmds.delete(transform)

        self.store("shapes", tuple([shape]), append=True)

        # Add attributes
        libattr.add_double(self.get_node(), "guideScale", min=0.01, dv=1)
        libattr.add_enum(self.get_node(), "guideAimAt", enums=Guide.DEFAULT)

        libattr.add_bool(self.get_node(), "guideAimFlip")
        libattr.add_enum(self.get_node(), "guideAimOrient", enums=Guide.ORIENT.keys())
        libattr.add_bool(self.get_node(), "guideDebug", dv=1)
        libattr.add_vector(self.get_node(), "guideOffsetOrient")

        for attr in ["guideScale", "guideAimOrient", "guideAimFlip", "guideAimAt",
                     "guideOffsetOrientX", "guideOffsetOrientY", "guideOffsetOrientZ",
                     "guideDebug"]:
            libattr.set(self.get_node(), attr, keyable=False, channelBox=True)

    def __create_aim(self):
        name = libname.rename(self.get_node(), suffix="aim")
        aim = cmds.createNode("transform", name=name)
        libattr.set(aim, "translateZ", -0.00000001)
        setup_node = self.get_setup()
        cmds.parent(aim, setup_node)
        self.store("aim", aim)

    def __create_up(self):
        up = Up(self)
        up.create()
        setup_node = self.get_setup()
        cmds.parent(up.get_group(), setup_node)

    def __create_scale(self):
        shapes = self.get_shapes()
        cl, cl_handle = cmds.cluster(shapes)
        libattr.set(cl, "relative", True)
        cl_handle = cmds.rename(cl_handle, libname.rename(self.get_node(), append="scale", suffix="clh"))
        self.store("scale", cl_handle)

        for axis in AXIS:
            cmds.connectAttr("{node}.guideScale".format(node=self.get_node()),
                             "{handle}.scale{axis}".format(handle=cl_handle, axis=axis))

        setup_node = self.get_setup()
        cmds.parent(cl_handle, setup_node)

    def __setup_network(self):

        aim = self.get_aim()
        cmds.connectAttr("{node}.guideDebug".format(node=self.get_node()),
                         "{aim}.displayLocalAxis".format(aim=aim))

        # Create main aim constraint
        aim_constraint = cmds.aimConstraint(self.get_node(),
                                            aim,
                                            worldUpObject=self.get_up().node,
                                            offset=(0, 0, 0),
                                            aimVector=(1, 0, 0),
                                            upVector=(0, 1, 0),
                                            worldUpType='object')[0]

        aim_handler = libconstraint.get_handler(aim_constraint)

        # Make main aim_cond
        aim_condition = cmds.createNode("condition", name=libname.rename(self.get_node(), suffix="cond", append="aim"))

        # Create local orient
        setup_node = self.get_setup()
        orient_constraint = cmds.orientConstraint(self.get_node(), setup_node, mo=True)[0]
        orient_aliases = aim_handler.aliases
        orient_targets = aim_handler.targets
        orient_index = orient_targets.index(self.get_node())

        aim_aliases = aim_handler.aliases
        aim_index = orient_targets.index(self.get_node())

        # Create 'custom' condition
        libattr.set(aim_condition, "secondTerm", Guide.DEFAULT.index("custom"))
        libattr.set(aim_condition, "colorIfTrueR", 1)
        libattr.set(aim_condition, "colorIfFalseR", 0)
        libattr.set(aim_condition, "operation", 5)
        cmds.connectAttr("%s.guideAimAt" % self.get_node(), "%s.firstTerm" % aim_condition)
        cmds.connectAttr("%s.outColorR" % aim_condition, "%s.%s" % (orient_constraint, orient_aliases[orient_index]))
        cmds.connectAttr("%s.outColorR" % aim_condition, "%s.%s" % (aim_constraint, aim_aliases[aim_index]))

        # self.__constraints["aim"] = libconstraint.get_handler(aim_constraint)

        # Create custom aim constraint offsets
        offset_pma = cmds.createNode("plusMinusAverage",
                                     name=libname.rename(self.get_node(), suffix="pma", append="custom"))

        cmds.connectAttr("{pma}.output3D".format(pma=offset_pma),
                         "{constraint}.offset".format(constraint=aim_constraint))

        for pair_index, axises in enumerate(Guide.ORIENT):

            primary, secondary = self.ORIENT[axises]

            # Axis condition
            pair_cond = cmds.createNode("condition", name=libname.rename(self.get_node(), append="aim%s" % pair_index, suffix="cond"))

            cmds.connectAttr("%s.guideAimOrient" % self.get_node(), "%s.firstTerm" % pair_cond)
            cmds.connectAttr("%s.outColor" % pair_cond, "%s.input3D[%s]" % (offset_pma, pair_index))

            libattr.set(pair_cond, "secondTerm", pair_index)
            libattr.set(pair_cond, "colorIfFalse", *(0, 0, 0), type="float3")

            # Flip condition
            flip_cond = cmds.createNode("condition", name=libname.rename(self.get_node(), append="aim%sFlip" % pair_index, suffix="cond"))
            cmds.connectAttr("%s.guideAimFlip" % self.get_node(), "%s.firstTerm" % flip_cond)
            cmds.connectAttr("%s.outColor" % flip_cond, "%s.colorIfTrue" % pair_cond)

            libattr.set(flip_cond, "secondTerm", 1)
            libattr.set(flip_cond, "colorIfTrue", *secondary, type="float3")
            libattr.set(flip_cond, "colorIfFalse", *primary, type="float3")

        # Add custom orient offset
        local_condition = cmds.createNode("condition")
        cmds.connectAttr("%s.guideAimAt" % self.get_node(), "%s.firstTerm" % local_condition)
        libattr.set(local_condition, "secondTerm", Guide.DEFAULT.index("custom"))
        libattr.set(local_condition, "operation", 0)
        for attr, axis, rgb in zip(["guideOffsetOrientX", "guideOffsetOrientY", "guideOffsetOrientZ"], AXIS, ["R", "G", "B"]):
            libattr.set(local_condition, "colorIfFalse%s" % rgb, 0)
            cmds.connectAttr("%s.%s" % (self.get_node(), attr), "%s.colorIfTrue%s" % (local_condition, rgb))
            cmds.connectAttr("%s.outColorR" % local_condition,
                             "%s.input3D[%s].input3D%s" % (offset_pma,
                                                           (pair_index + 1),
                                                           axis.lower()))

        self.store("aim_constraint", aim_constraint, dag=False)
        self.store("aim_condition", aim_condition, dag=False)
        self.store("orient_constraint", orient_constraint, dag=False)

    def _create(self):

        self.__create_node()
        self.__create_setup()
        self.__create_aim()
        self.__create_up()
        self.__create_scale()

        self.__setup_network()

        # Lock up some attributes
        libattr.lock_rotate(self.get_node())
        libattr.lock_scale(self.get_node())
        libattr.lock_visibility(self.get_node())


class Up(Module):

    SUFFIX = "up"
    RAIDUS = 0.3

    def __init__(self, guide):

        self.__guide = guide

        super(Up, self).__init__(*guide.tokens)

    def get_position(self, worldspace=True):
        position = []
        if self.exists:
            position = cmds.xform(self.get_node(), q=True, ws=worldspace, t=True)
        return tuple(position)

    def get_guide(self):
        return self.__guide

    def get_group(self):
        return self._dag.get("grp")

    def get_shapes(self):
        return self._dag.get("shapes")

    def __create_node(self):
        grp_name = libname.rename(self.get_name().compile(), append="Up", suffix="grp")
        grp = cmds.createNode("transform", name=grp_name)
        self.store("grp", grp)

        sphere = cmds.sphere(name=self.get_name().compile(), radius=Up.RAIDUS)[0]
        shapes = cmds.listRelatives(sphere, shapes=True)

        cmds.parent(sphere, grp)

        # Add attributes
        libattr.add_double(self.get_node(), "guideScale", min=0.01, dv=1)

        for attr in ["guideScale"]:
            libattr.set(self.get_node(), attr, keyable=False, channelBox=True)

        guide = self.get_guide()
        for axis in AXIS:
            cmds.connectAttr("{node}.guideScale".format(node=guide.node),
                             "{grp}.scale{axis}".format(grp=grp, axis=axis))

        self.store("node", sphere)
        self.store("shapes", shapes, append=shapes)

    def __create_scale(self):
        shapes = self.get_shapes()
        cl, cl_handle = cmds.cluster(shapes)
        libattr.set(cl, "relative", True)
        cl_handle = cmds.rename(cl_handle, libname.rename(self.get_node(), append="upScale", suffix="clh"))
        self.store("scale", cl_handle)

        for axis in AXIS:
            cmds.connectAttr("{node}.guideScale".format(node=self.get_node()),
                             "{handle}.scale{axis}".format(handle=cl_handle, axis=axis))

        group = self.get_group()
        cmds.parent(cl_handle, group)

    def _create(self):
        self.__create_node()
        self.__create_scale()

        libattr.set(self.get_node(), "translateY", 3)

    def _post(self):
        super(Up, self)._post()

        # Lock up some attributes
        libattr.lock_rotate(self.get_node())
        libattr.lock_scale(self.get_node())
        libattr.lock_visibility(self.get_node())


class Tendon(Module):

    SUFFIX = "cncShape"

    def __init__(self, child, parent):

        self.__child = child
        self.__parent = parent

        super(Tendon, self).__init__(*child.tokens)

    @property
    def condition(self):
        return self._nondag.get("condition")

    @property
    def child(self):
        return self.__child

    @property
    def parent(self):
        return self.__parent

    def __create_annotation(self):
        shape = cmds.createNode("annotationShape", name=self.get_node())
        transform = cmds.listRelatives(shape, parent=True)[0]

        parent = self.get_parent()
        cmds.parent(self.get_node(), parent.node, shape=True, relative=True)
        cmds.delete(transform)

        libattr.set(self.get_node(), "overrideEnabled", True)
        libattr.set(self.get_node(), "overrideColor", 18)
        libattr.set(self.get_node(), "displayArrow", False)
        libattr.set(self.get_node(), "displayArrow", True)
        cmds.connectAttr("{src}.worldMatrix[0]".format(src=self.child.shapes[0]),
                         "{dst}.dagObjectMatrix[0]".format(dst=self.get_node()),
                         force=True)

    def __create_aim(self):

        parent = self.get_parent()

        # Query aliases and target list from parent aim constraint
        aim_handler = libconstraint.get_handler(parent.constraint)
        aliases = aim_handler.aliases
        targets = aim_handler.targets
        index = targets.index(self.child.aim)

        # Query parent joint enum items
        enums = cmds.attributeQuery("guideAimAt", node=parent.node, listEnum=True)[0].split(":")
        enum_index = enums.index(self.child.node)

        # Create condition that turns on aim for child constraint if
        # enum index is set to match childs name
        condition = cmds.createNode("condition", name=libname.rename(self.get_node(), append=self.description, suffix="cond"))

        libattr.set(condition, "secondTerm", enum_index)
        libattr.set(condition, "colorIfTrueR", 1)
        libattr.set(condition, "colorIfFalseR", 0)

        cmds.connectAttr("%s.guideAimAt" % parent.node, "%s.firstTerm" % condition)
        cmds.connectAttr("%s.outColorR" % condition, "%s.%s" % (parent.get_constraint(), aliases[index]))

        # Set enum to match child aim
        libattr.set(parent.node, "guideAimAt", enum_index)

        # Loop through all aliases on and set non-connected attributes to be 0
        for alias in aliases:
            if not cmds.listConnections('%s.%s' % (parent.get_constraint(), alias),
                                        source=True,
                                        destination=False,
                                        plugs=True):
                libattr.set(parent.get_constraint(), alias, 0)

        # Store new condition
        self.store("condition", condition, dag=False)

    def __update_aim_index(self):
        if self.exists:

            # Query parent joint enum items
            enums = cmds.attributeQuery("guideAimAt", node=self.__parent.node, listEnum=True)[0].split(':')
            enum_index = enums.index(self.__child.node)

            # Update index to reflect alias index of child
            parent = self.get_parent()
            libattr.set(parent.get_condition(), "secondTerm", enum_index)

    def _create(self):
        self.__create_annotation()
        self.__create_aim()
