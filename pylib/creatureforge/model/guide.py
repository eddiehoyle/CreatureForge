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
from creatureforge.model.base import Module
from creatureforge.exceptions import DuplicateNameError
from creatureforge.exceptions import InvalidNameError
from creatureforge.exceptions import InvalidGuideError
from creatureforge.exceptions import GuideDoesNotExistError

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

AXIS = ["X", "Y", "Z"]


def exists(func):
    def wraps(*args, **kwargs):
        node = args[0].node
        if libname.is_valid(node):
            return cmds.objExists(str(Guide(*libname.tokens(node))))
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
            msg = "'%s' is not a valid guide." % node
            logger.error(msg)
            raise TypeError(msg)
        # try:
        #     if libname.is_valid(node):
        #         return Guide(*libname.tokens(str(node))).reinit()
        # except InvalidNameError:
        #     err = "Node is node a valid guide: {node}".format(node=node)
        #     raise InvalidGuideError(err)

    def __init__(self, position, description, index=0):
        super(Guide, self).__init__(position, description, index)

        self.__constraints = {}
        self.__connectors = []

    def reinit(self):
        super(Guide, self).reinit()

        self.store("up", Up(self))

        return self

    @property
    def connectors(self):
        return self.__connectors

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
        return self._nondag.get("aim_constraint")

    @property
    def condition(self):
        return self._nondag.get("aim_condition")

    @property
    def parent(self):
        parent = cmds.listRelatives(self.node, parent=True, type="joint")
        if parent:
            return Guide.validate(parent[0])
        return None

    @property
    def children(self):
        if self.exists:
            children = cmds.listRelatives(self.node, children=True, type="joint") or []
            if children:
                return map(Guide.validate, children)
        return []

    @property
    def primary(self):
        if self.exists:
            order = Guide.ORIENT.keys()
            axis = order[cmds.getAttr("{node}.guideAimOrient".format(node=self.node))][0]
            return axis.upper()
        return None

    @property
    def secondary(self):
        if self.exists:
            order = Guide.ORIENT.keys()
            axis = order[cmds.getAttr("{node}.guideAimOrient".format(node=self.node))][1]
            return axis.upper()
        return None

    def set_position(self, x, y, z, worldspace=False):
        if self.exists:
            logger.debug("Setting '%s' position: %s" % (self.node, [x, y, z]))
            cmds.xform(self.node, ws=worldspace, t=[x, y, z])

    def copy(self):
        name = libname.generate(self.node)
        return Guide(*libname.tokens(name)).create()

    def has_parent(self, guide):
        guide = Guide.validate(guide)
        parent = self.parent
        while parent:
            if guide.node == parent.node:
                return True
            parent = parent.parent
        return False

    def has_child(self, guide):
        if self.exists:
            return Guide.validate(guide) in self.children
        return False

    def remove_parent(self):
        if self.exists:
            if self.parent:
                self.parent.__remove_aim(self)

    def add_child(self, guide):

        t = time.time()

        guide = Guide.validate(guide)

        # Try to parent to itself
        if self.node == guide.node:
            logger.warning("Cannot add '%s' to itself as child" % self.node)
            return None

        # Guide is already a child of self
        if self.has_child(guide):
            logger.info("'%s' is already a child of '%s'" % (guide.node, self.node))
            return self.children.index(guide.node)

        # If guide has any parent already
        if guide.parent:
            guide.remove_parent()

        # Is guide above self in hierarchy
        print "%s has parent: %s" % (self, self.has_parent(guide))
        if self.has_parent(guide):
            self.remove_parent()

        self.__add_aim(guide)
        logger.info("'%s' successfully added child: '%s' (%0.3fs)" % (self.node,
                                                                      guide.node,
                                                                      time.time()-t))
        return guide

    def set_parent(self, guide):

        guide = Guide.validate(guide)

        t = time.time()

        # Try to parent to itself
        if self == guide:
            logger.warning("Cannot parent '%s' to itself" % self.node)
            return None

        # Is guide already parent
        if self.parent == guide:
            logger.debug("'%s' is already a parent of '%s'" % (guide.node, self.node))
            return self.parent

        # Is guide below self in hierarchy
        if guide.has_parent(self):
            guide.remove_parent()

        # If self has any parent already
        if self.parent:
            self.remove_parent()

        guide.__add_aim(self)
        logger.info("'%s' successfully set parent: '%s' (%0.3fs)" % (self.node,
                                                                     guide.node,
                                                                     time.time()-t))

        return guide

    def __add_aim(self, guide):
        """
        Private aim creation method. Add the input guide as a child
        by extending this guides aimConstraint values and adding
        an aim enum value to the 'aimAt' attribute.
        """

        cmds.aimConstraint(guide.aim, self.aim,
                           worldUpObject=self.up.node,
                           worldUpType="object",
                           aimVector=(1, 0, 0),
                           upVector=(0, 1, 0),
                           mo=False)

        # Edit aim attribute on node to include new child
        enums = cmds.attributeQuery("guideAimAt", node=self.node, listEnum=True)[0].split(":")
        enums.append(guide.node)
        libattr.edit_enum(self.node, "guideAimAt", enums=enums)

        # Create connector
        con = Tendon(guide, self)
        con.create()

        self.__connectors.append(con)
        print self.__connectors

        # Parent new guide under self
        cmds.parent(guide.node, self.node, a=True)

        return guide

    def __remove_aim(self, guide):

        t = time.time()

        if not self.has_child(guide):
            raise ValueError("Guide '%s' is not a child of '%s'" % (guide.node, self.node))

        print 'removing %s as parent from %s' % (self, guide)

        # Remove connector
        connectors = self.connectors
        print connectors
        for con in connectors:
            print con.parent, self
            if con.parent == self:
                con.remove()
                connectors.remove(con)
                break

        # Parent guide to world
        cmds.parent(guide.node, world=True)

        # Remove enum name
        enums = cmds.attributeQuery("guideAimAt", node=self.node, listEnum=True)[0].split(":")
        enums.remove(guide.node)
        libattr.edit_enum(self.node, "guideAimAt", enums)
        libattr.set(self.node, "guideAimAt", len(enums) - 1)

        aliases = cmds.aimConstraint(self.constraint, q=True, wal=True)
        for alias in aliases:
            if not cmds.listConnections("%s.%s" % (self.constraint, alias),
                                        source=True,
                                        destination=False,
                                        plugs=True):
                libattr.set(self.constraint, alias, 0)

        # Default to world if no aim objects are attached
        if len(enums) == len(Guide.DEFAULT):
            libattr.set(self.node, "guideAimAt", 0)

        logger.debug("'%s' remove child: '%s' (%0.3fs)" % (self.node,
                                                           guide.node,
                                                           time.time() - t))

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
        libattr.add_enum(self.node, "guideAimAt", enums=Guide.DEFAULT)

        libattr.add_bool(self.node, "guideAimFlip")
        libattr.add_enum(self.node, "guideAimOrient", enums=Guide.ORIENT.keys())
        libattr.add_bool(self.node, "guideDebug", dv=1)
        libattr.add_vector(self.node, "guideOffsetOrient")

        for attr in ["guideScale", "guideAimOrient", "guideAimFlip", "guideAimAt",
                     "guideOffsetOrientX", "guideOffsetOrientY", "guideOffsetOrientZ",
                     "guideDebug"]:
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

        cmds.connectAttr("{node}.guideDebug".format(node=self.node),
                         "{aim}.displayLocalAxis".format(aim=self.aim))

        # Create main aim constraint
        aim_constraint = cmds.aimConstraint(self.node,
                                            self.aim,
                                            worldUpObject=self.up.node,
                                            offset=(0, 0, 0),
                                            aimVector=(1, 0, 0),
                                            upVector=(0, 1, 0),
                                            worldUpType='object')[0]

        aim_handler = libconstraint.get_handler(aim_constraint)

        # Make main aim_cond
        aim_condition = cmds.createNode("condition", name=libname.rename(self.node, suffix="cond", append="aim"))

        # Create local orient
        orient_constraint = cmds.orientConstraint(self.node, self.setup, mo=True)[0]
        orient_aliases = aim_handler.aliases
        orient_targets = aim_handler.targets
        orient_index = orient_targets.index(self.node)

        aim_aliases = aim_handler.aliases
        aim_targets = aim_handler.targets
        aim_index = orient_targets.index(self.node)

        # Create 'custom' condition
        libattr.set(aim_condition, "secondTerm", Guide.DEFAULT.index("custom"))
        libattr.set(aim_condition, "colorIfTrueR", 1)
        libattr.set(aim_condition, "colorIfFalseR", 0)
        libattr.set(aim_condition, "operation", 5)
        cmds.connectAttr("%s.guideAimAt" % self.node, "%s.firstTerm" % aim_condition)
        cmds.connectAttr("%s.outColorR" % aim_condition, "%s.%s" % (orient_constraint, orient_aliases[orient_index]))
        cmds.connectAttr("%s.outColorR" % aim_condition, "%s.%s" % (aim_constraint, aim_aliases[aim_index]))

        self.__constraints["aim"] = libconstraint.get_handler(aim_constraint)

        # Create custom aim constraint offsets
        offset_pma = cmds.createNode("plusMinusAverage",
                                     name=libname.rename(self.node, suffix="pma", append="custom"))

        cmds.connectAttr("{pma}.output3D".format(pma=offset_pma),
                         "{constraint}.offset".format(constraint=aim_constraint))

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
        local_condition = cmds.createNode("condition")
        cmds.connectAttr("%s.guideAimAt" % self.node, "%s.firstTerm" % local_condition)
        libattr.set(local_condition, "secondTerm", Guide.DEFAULT.index("custom"))
        libattr.set(local_condition, "operation", 0)
        for attr, axis, rgb in zip(["guideOffsetOrientX", "guideOffsetOrientY", "guideOffsetOrientZ"], AXIS, ["R", "G", "B"]):
            libattr.set(local_condition, "colorIfFalse%s" % rgb, 0)
            cmds.connectAttr("%s.%s" % (self.node, attr), "%s.colorIfTrue%s" % (local_condition, rgb))
            cmds.connectAttr("%s.outColorR" % local_condition,
                             "%s.input3D[%s].input3D%s" % (offset_pma,
                                                           (pair_index + 1),
                                                           axis.lower()))

        self.store("aim_constraint", aim_constraint, dag=False)
        self.store("aim_condition", aim_condition, dag=False)
        self.store("orient_constraint", orient_constraint, dag=False)

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

        # Lock up some attributes
        libattr.lock_rotate(self.node)
        libattr.lock_scale(self.node)
        libattr.lock_visibility(self.node)

    def remove(self):

        if not self.exists:
            err = "Guide does not exist: {node}".format(node=self.node)
            raise GuideDoesNotExistError(err)

        nodes = []
        nodes.extend(list(libutil.flatten(self.dag.values())))
        nodes.extend(list(libutil.flatten(self.nondag.values())))

        cmds.delete(nodes)


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
    def condition(self):
        return self._nondag.get("condition")

    @property
    def child(self):
        return self.__child

    @property
    def parent(self):
        return self.__parent

    def remove(self):
        1/0

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

    def __create_aim(self):

        # Query aliases and target list from parent aim constraint
        aim_handler = libconstraint.get_handler(self.parent.constraint)
        aliases = aim_handler.aliases
        targets = aim_handler.targets
        index = targets.index(self.child.aim)

        # aliases = cmds.aimConstraint(self.parent.constraint, q=True, wal=True)
        # targets = cmds.aimConstraint(self.parent.constraint, q=True, tl=True)
        # index = targets.index(self.child.aim)

        # Query parent joint enum items
        enums = cmds.attributeQuery("guideAimAt", node=self.parent.node, listEnum=True)[0].split(":")
        enum_index = enums.index(self.child.node)

        # Create condition that turns on aim for child constraint if
        # enum index is set to match childs name
        condition = cmds.createNode("condition", name=libname.rename(self.node, append=self.description, suffix="cond"))

        libattr.set(condition, "secondTerm", enum_index)
        libattr.set(condition, "colorIfTrueR", 1)
        libattr.set(condition, "colorIfFalseR", 0)

        cmds.connectAttr("%s.guideAimAt" % self.parent.node, "%s.firstTerm" % condition)
        cmds.connectAttr("%s.outColorR" % condition, "%s.%s" % (self.parent.constraint, aliases[index]))

        # Set enum to match child aim
        libattr.set(self.parent.node, "guideAimAt", enum_index)

        # Loop through all aliases on and set non-connected attributes to be 0
        for alias in aliases:
            if not cmds.listConnections('%s.%s' % (self.parent.constraint, alias),
                                        source=True,
                                        destination=False,
                                        plugs=True):
                libattr.set(self.parent.constraint, alias, 0)

        # Store new condition
        self.store("condition", condition, dag=False)

    def __update_aim_index(self):
        if self.exists:

            # Query parent joint enum items
            enums = cmds.attributeQuery("guideAimAt", node=self.__parent.node, listEnum=True)[0].split(':')
            enum_index = enums.index(self.__child.node)

            # Update index to reflect alias index of child
            libattr.set(self.parent.aim_cond, "secondTerm", enum_index)

    def _create(self):
        self.__create_annotation()
        self.__create_aim()
