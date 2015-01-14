#!/usr/bin/env python

"""
Guide model
"""

import time
import json
from maya import cmds

from collections import OrderedDict
from crefor.lib import libName, libShader, libAttr
from crefor.model import Node
from crefor.model.guide.connector import Connector
from crefor.model.guide.up import Up
from crefor import log

logger = log.get_logger(__name__)

__all__ = ["Guide"]

class Guide(Node):
    """
    Guide model

    :param      position:           L, R, C, etc
    :type       position:           str
    :param      description:        Description of guide
    :type       description:        str
    :param      index:              Inde of guide
    :type       index:              str
    :returns:                       Guide object
    :rtype:                         Guide

    **Example**:

    >>> Guide("C", "spine", index=0)
    # Result: <Guide 'C_spine_0_gde'> #
    """

    SEP = "_"
    SUFFIX = 'gde'
    RADIUS = 1.0
    DEFAULT_AIMS = ["world"]
    UP_SCALE_VALUE = RADIUS/3.3

    AIM_ORIENT = OrderedDict([("xyz", [(0, 0, 0), (0, 180, 0)]),
                             ("xzy", [(-90, 0, 0), (-90, 180, 0)]),
                             ("yxz", [(0, -180, -90), (0, 0, 90)]),
                             ("yzx", [(0, -90, -90), (180, 90, -90)]),
                             ("zxy", [(-90, 180, -90), (90, 180, -90)]),
                             ("zyx", [(-90, 90, -90), (-90, -90, 90)])])

    # AIM_ORIENT = OrderedDict([("xy", [(0, 0, 0), (0, 180, 0)]),
    #                          ("xz", [(-90, 0, 0), (-90, 180, 0)]),
    #                          ("yx", [(0, -180, -90), (0, 0, 90)]),
    #                          ("yz", [(0, -90, -90), (180, 90, -90)]),
    #                          ("zx", [(-90, 180, -90), (90, 180, -90)]),
    #                          ("zy", [(-90, 90, -90), (-90, -90, 90)])])

    @staticmethod
    def validate(guide):
        """validate(guide)
        """

        if isinstance(guide, Guide):
            return guide
        else:
            try:
                return Guide(*libName.decompile(str(guide), 3)).reinit()
            except Exception as e:
                logger.error("Failed to initialise node as guide: '%s'" % guide)
                raise

    def __init__(self, position, description, index=0):
        super(Guide, self).__init__(position, description, index)

        # Constraint utils
        self.up = None
        self.aim = None

        # Constraint default options
        self.world = None
        self.custom = None

        # Aim constraint
        self.constraint = None
        self.orient = None

        self.__trash = []

        self.__nodes = {}
        self.__nondag = []

    def create(self):
        """create()
        """

        if self.exists():
            msg = "Cannot create guide '%s', already exists." % (self.node)
            logger.error(msg)
            raise RuntimeError(msg)

        t = time.time()

        self.__create_nodes()
        self.__create_up()
        self.__create_aim()
        self.__create_shader()
        self.__post()

        logger.info("Guide created: '%s' (%0.3fs)" % (self.node,
                                                     time.time()-t))

        return self

    def reinit(self):
        """reinit()
        """

        if not self.exists():
            raise Exception('Cannot reinit \'%s\' as guide does not exist.' % self.node)

        # Get setup node
        for key, item in self.nodes.items():
            setattr(self, key, item)

        self.up = Up(self).reinit()

        # Get snapshot
        self.__nodes = json.loads(cmds.getAttr("%s.nodes" % self.node))
        self.__nondag = json.loads(cmds.getAttr("%s.nondag" % self.node))

        return self

    def duplicate(self):
        """duplicate()
        """

        name = libName.generate(self.node)
        return Guide(*libName.decompile(name, 3)).create()

    def remove(self):
        """
        """

        if self.exists():

            self.strip()

            self.up.remove()

            cmds.delete(self.nondag)
            cmds.delete(self.setup)
            cmds.delete(self.node)

    def compile(self):
        """
        Compile guide into a node
        """

        joint = None
        if self.exists():
            cmds.select(cl=True)

            # Get some joint creation args
            orientation = cmds.xform(self.aim, q=1, ws=1, ro=1)
            rotationOrder = self.AIM_ORIENT.keys()[cmds.getAttr("%s.aimOrient" % self.node)]

            # Create joint
            joint = cmds.joint(name=libName.update(self.node, suffix="jnt"),
                               orientation=orientation,
                               position=self.get_position(),
                               rotationOrder=rotationOrder)

            cmds.select(cl=True)
            logger.debug("Compiled guide '%s' into node: '%s'" % (self.node, joint))

        return joint

    # ======================================================================== #
    # Aim
    # ======================================================================== #

    def flip(self):
        """
        """

        if self.exists() and self.up.exists():

            aim_at = cmds.getAttr("%s.aimAt" % self.node)
            if aim_at >= len(Guide.DEFAULT_AIMS):
                self.up.flip()

    def flop(self):
        """
        """

        if self.exists() and self.up.exists():

            aim_at = cmds.getAttr("%s.aimAt" % self.node)
            if aim_at >= len(Guide.DEFAULT_AIMS):
                self.up.flop()

    # ======================================================================== #
    # Properties
    # ======================================================================== #

    @property
    def nodes(self):
        """nodes()
        Return important nodes from Guide class

        :returns:   Dictionary of important nodes in {"attr": "value"} format
        :rtype:     dict

        **Example**:

        >>> arm = Guide("L", "arm", 0).create()
        >>> arm.nodes
        # Result: {u'nondag': [u'L_armLocal_0_cond'], "...": "..."} # 
        """

        if self.exists():
            if not self.__nodes:
                self.__nodes = json.loads(cmds.getAttr("%s.nodes" % self.node))
            return self.__nodes
        return {}

    @property
    def nondag(self):
        """nodes(self)
        Return important nodes from Guide class

        :returns:   Dictionary of important nodes in {"attr": "value"} format
        :rtype:     dict

        **Example**:

        >>> arm = Guide("L", "arm", 0).create()
        >>> arm.nodes
        # Result: {u'nondag': [u'L_armLocal_0_cond'], "...": "..."} # 
        """

        if self.exists():
            if not self.__nondag:
                self.__nondag = json.loads(cmds.getAttr("%s.nondag" % self.node))
            return self.__nondag
        return {}

    @property
    def short_name(self):
        """
        Short name of guide
        """

        if self.exists():
            return cmds.ls(self.node, long=True)[0].split('|')[-1]
        else:
            logger.warning("Guide '%s' does not exist." % self.node)
            return None

    @property
    def long_name(self):
        """
        Long name of guide
        """

        if self.exists():
            return cmds.ls(self.node, long=True)[0]
        else:
            logger.warning("Guide '%s' does not exist." % self.node)
            return None

    @property
    def parent(self):
        """
        Get parent node and return guide object
        """

        _parent = cmds.listRelatives(self.node, parent=True, type="joint") if self.exists() else None
        if _parent:
            return Guide.validate(_parent[0])
        return None

    @property
    def children(self):
        """
        Get children nodes and return dict with guide objects
        """


        _children = cmds.listRelatives(self.node, children=True, type="joint") or []
        children = []
        for child in _children:
            children.append(Guide.validate(child))
        return children

    @property
    def connectors(self):
        """
        Connectors are stored in sync with children
        """

        connectors = []
        for child in self.children:
            connectors.append(Connector(self, child).reinit())
        return connectors

    @property
    def primary(self):
        """
        """

        if self.exists():
            order = self.AIM_ORIENT.keys()
            return order[cmds.getAttr("%s.aimOrient" % self.node)][0]
        return None

    @property
    def secondary(self):
        """
        """

        if self.exists():
            order = self.AIM_ORIENT.keys()
            return order[cmds.getAttr("%s.aimOrient" % self.node)][1]
        return None

    # ======================================================================== #
    # Setters
    # ======================================================================== #

    def set_axis(self, primary, secondary):
        """
        """

        if self.exists():

            if str(primary).lower() == str(secondary).lower():
                msg = ("Cannot set both primary and secondary orient " \
                       "as the same axis: %s, %s" % (primary, secondary))
                raise ValueError(msg)

            base = list(self.AIM_ORIENT.keys()[0])

            try:
                base.pop(base.index(str(primary).lower()))
                base.pop(base.index(str(secondary).lower()))
                axis = "".join([primary, secondary, "".join(base)]).lower()
                cmds.setAttr("%s.aimOrient" % self.node, self.AIM_ORIENT.keys().index(axis))

            except Exception:
                msg = "Primary and/or secondary axis not valid: %s, %s" % (primary, secondary)
                raise ValueError(msg)

    def set_scale(self, value):
        """
        Scale guide and related connectors
        """

        selected = cmds.ls(sl=1)
        if self.node:
            cls, clh = cmds.cluster(self.shapes)
            cmds.setAttr('%s.scale' % clh, value, value, value, type='float3')
            cmds.delete(self.shapes, ch=True)

        for con in self.connectors:
            con.set_start_scale(value)

        if selected:
            cmds.select(selected, r=True)

    def aim_at(self, guide, add=False):
        """
        Aim at input guide if it is a child. If not, then use the
        add boolean argument to create as a child and aim at it.
        """

        if self.exists():

            enums = cmds.attributeQuery("aimAt", node=self.node, listEnum=True)[0].split(":")

            # Get world, local keywords first
            if guide in self.DEFAULT_AIMS:
                cmds.setAttr("%s.aimAt" % self.node, enums.index(guide))
                return

            # Try validate guide
            try:
                guide = Guide.validate(guide)
            except Exception:
                msg = "Cannot aim '%s' at '%s' as it does not exist." % (self, guide)
                logger.error(msg)
                raise RuntimeError(msg)

            # Aim guide at child, or create and aim
            if not self.has_child(guide):
                if add:
                    self.add_child(guide)
                else:
                    raise RuntimeError("Guide '%s' is not a child of '%s'" % (guide.node, self.node))

            enums = cmds.attributeQuery("aimAt", node=self.node, listEnum=True)[0].split(":")
            cmds.setAttr("%s.aimAt" % self.node, enums.index(guide.aim))

    def aim_flip(self, value):
        """
        """

        if self.exists():
            cmds.setAttr("%s.aimFlip" % self.node, bool(value))

    def set_position(self, vector3f, local=False):
        """
        Set position of guide
        """

        if self.exists():
            logger.debug("Setting '%s' position: %s" % (self.node, vector3f))
            cmds.xform(self.node, ws=not local, t=vector3f)

    def set_debug(self, debug):
        """
        Set debug visibility
        """

        if self.exists():
            cmds.setAttr('%s.debug' % self.node, bool(debug))

    # ======================================================================== #
    # Getters
    # ======================================================================== #

    def get_axis(self):
        """
        """

        if self.exists():
            order = self.AIM_ORIENT.keys()
            return order[cmds.getAttr("%s.aimOrient" % self.node)]
        return None

    def get_position(self, local=False):
        """
        """

        return cmds.xform(self.node,
                          q=True,
                          ws=not local,
                          t=True) if self.exists() else None

    def get_up_position(self, local=False):
        """
        """

        return self.up.get_position(local) if self.exists() else None

    def get_aim_at(self):
        """
        """

        if self.exists():
            enums = cmds.attributeQuery('aimAt', node=self.node, listEnum=True)[0].split(':')
            return enums[cmds.getAttr("%s.aimAt" % self.node)]
        else:
            return None

    def get_child(self, guide):
        """
        """

        guide = Guide.validate(guide)
        try:
            return self.children.index(guide.node)
        except Exception:
            msg = "Guide '%s' is not a child of: '%s'" % (guide.node, self.node)
            logger.error(msg)
            raise RuntimeError(msg)

    def snapshot(self):
        """snapshot()
        Get a dictionary snapshot of guide data.

        :returns:           Dictionary of relevant guide information
        :rtype:             dict

        **Example**:

        >>> root = Guide("C", "root", 0)
        >>> root.snapshot()
        """

        return dict(node=self.node,
                    parent=self.parent.node if self.parent else None,
                    children=[c.node for c in self.children],
                    aim_at=self.get_aim_at(),
                    aim_flip=bool(cmds.getAttr("%s.aimFlip" % self.node)),
                    position=self.get_position(local=False),
                    up_position=self.get_up_position(local=False),
                    primary=self.primary,
                    secondary=self.secondary) if self.exists() else {}

    # ======================================================================== #
    # Public
    # ======================================================================== #

    def strip(self):
        """strip()
        Strip node of all hierarchy
        """

        if self.exists():

            parent = self.parent
            if self.parent:
                self.remove_parent()

            children = self.children
            if children:
                for child in children:
                    self.remove_child(child)

    def has_child(self, guide):
        """
        Is guide an immediate child of self
        """

        return Guide.validate(guide).node in [g.node for g in self.children]

    def is_parent(self, guide):
        """
        Is guide the immediate parent of self
        """

        if self.parent:
            return Guide.validate(guide).node == self.parent.node
        return False

    def has_parent(self, guide):
        """
        Iterate over all parents to see if guide is one
        """

        guide = Guide.validate(guide)
        parent = self.parent
        while parent:
            if guide.node == parent.node:
                return True
            parent = parent.parent
        return False

    def set_parent(self, guide):
        """
        Set guide to be parent of self
        """

        t = time.time()

        guide = Guide.validate(guide)

        # Try to parent to itself
        if self.node == guide.node:
            logger.warning("Cannot parent '%s' to itself" % self.node)
            return None

        # Is guide already parent
        if self.parent and self.parent.node == guide.node:
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

    def add_child(self, guide):
        """
        Add guide to children
        """

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
        if self.has_parent(guide):
            self.remove_parent()

        self.__add_aim(guide)
        logger.info("'%s' successfully added child: '%s' (%0.3fs)" % (self.node,
                                                                      guide.node,
                                                                      time.time()-t))
        return guide

    def remove_parent(self):
        """
        If have a parent, tell parent to remove aim to self
        """

        if self.parent:
            self.parent.__remove_aim(self)

    def remove_child(self, guide):
        """
        """

        self.__remove_aim(guide)

    # ======================================================================== #
    # Private
    # ======================================================================== #

    def __add_aim(self, guide):
        """
        Create a new child aim relationship between self and guide.
        Guide is considered to be the child of self. Any constraint
        and attribute updates are added to self, as well as the connector.
        """

        guide = Guide.validate(guide)

        cmds.aimConstraint(guide.aim, self.aim, worldUpObject=self.up.node,
                           worldUpType='object',
                           aimVector=(1, 0, 0),
                           upVector=(0, 1, 0),
                           mo=False)

        # Edit aim attribute on node to include new child
        enums = cmds.attributeQuery('aimAt', node=self.node, listEnum=True)[0].split(':')
        enums.append(guide.aim)
        cmds.addAttr('%s.aimAt' % self.node, e=True, en=':'.join(enums))

        # Create connector
        con = Connector(self, guide)
        con.create()

        # Parent new guide under self
        cmds.parent(guide.node, self.node, a=True)

        return guide

    def __remove_aim(self, guide):
        """
        self has guide as a child
        self has constraint
        self --> guide

        self is always parent
        guide is always child
        """

        t = time.time()

        guide = Guide.validate(guide)
        if not self.has_child(guide):
            return

        # Remove connector
        connectors = self.connectors
        for con in connectors:
            if con.parent == self:
                con.remove()
                connectors.remove(con)
                break

        # Parent guide to world
        cmds.parent(guide.node, world=True)
        enums = cmds.attributeQuery('aimAt', node=self.node, listEnum=True)[0].split(':')
        enums.remove(guide.aim)
        cmds.addAttr('%s.aimAt' % self.node, e=True, en=':'.join(enums))
        cmds.setAttr('%s.aimAt' % self.node, len(enums) - 1)

        aliases = cmds.aimConstraint(self.constraint, q=True, wal=True)
        for alias in aliases:
            if not cmds.listConnections('%s.%s' % (self.constraint, alias),
                                        source=True,
                                        destination=False,
                                        plugs=True):
                cmds.setAttr('%s.%s' % (self.constraint, alias), 0)

        # Default to world
        if len(enums) == 1:
            cmds.setAttr('%s.aimAt' % self.node, 0)

        # Reinit children
        for con in connectors:
            con.reinit()

        logger.debug("'%s' remove child: '%s' (%0.3fs)" % (self.node,
                                                           guide.node,
                                                           time.time()-t))


    def __create_nodes(self):
        
        # Create node and parent sphere under
        cmds.select(cl=True)
        self.node = cmds.joint(name=self.node)
        cmds.setAttr("%s.radius" % self.node, cb=False)
        cmds.setAttr("%s.radius" % self.node, l=True)
        cmds.select(cl=True)

        # Create attributes
        cmds.setAttr("%s.rotateOrder" % self.node, k=False)
        cmds.setAttr("%s.rotateOrder" % self.node, cb=True)

        cmds.addAttr(self.node, ln="guideScale", at="double", min=0.01, dv=1)
        cmds.setAttr("%s.guideScale" % self.node, k=False)
        cmds.setAttr("%s.guideScale" % self.node, cb=True)

        cmds.addAttr(self.node, ln='aimAt', at='enum', en=":".join(self.DEFAULT_AIMS))
        cmds.setAttr('%s.aimAt' % self.node, k=False)
        cmds.setAttr('%s.aimAt' % self.node, cb=True)

        cmds.addAttr(self.node, ln='aimOrient', at='enum', en=":".join(self.AIM_ORIENT.keys()))
        cmds.setAttr('%s.aimOrient' % self.node, k=False)
        cmds.setAttr('%s.aimOrient' % self.node, cb=True)

        cmds.addAttr(self.node, ln="aimFlip", at="bool", min=0, max=1, dv=0)
        cmds.setAttr("%s.aimFlip" % self.node, k=False)
        cmds.setAttr("%s.aimFlip" % self.node, cb=True)

        cmds.addAttr(self.node, ln="debug", at="bool", min=0, max=1, dv=0)
        cmds.setAttr("%s.debug" % self.node, k=False)
        cmds.setAttr("%s.debug" % self.node, cb=True)

        for key in ["nodes", "nondag"]:
            cmds.addAttr(self.node, ln=key, dt="string")
            cmds.setAttr("%s.%s" % (self.node, key), k=False)

        # Create shapes
        _sphere = cmds.sphere(radius=self.RADIUS, ch=False)[0]
        self.shapes = cmds.listRelatives(_sphere, type='nurbsSurface', children=True)
        cmds.parent(self.shapes, self.node, r=True, s=True)
        cmds.setAttr('%s.drawStyle' % self.node, 2)

        # Setup node
        self.setup = cmds.group(name=libName.update(self.node, suffix="setup"), empty=True)
        cmds.pointConstraint(self.node, self.setup, mo=False)

        # Create scale cluster
        _cl, _scale = cmds.cluster(self.shapes)
        cmds.setAttr("%s.relative" % _cl, True)
        self.scale = cmds.rename(_scale, libName.update(self.node, append="scale", suffix="clh"))
        cmds.parent(self.scale, self.setup)

        # Lock down scale
        for attr in ["translate", "rotate"]:
            for axis in ["X", "Y", "Z"]:
                cmds.setAttr("%s.%s%s" % (self.scale, attr, axis), k=False)
                cmds.setAttr("%s.%s%s" % (self.scale, attr, axis), l=True)
        cmds.setAttr("%s.visibility" % self.scale, 0)
        cmds.setAttr("%s.visibility" % self.scale, k=False)
        cmds.setAttr("%s.visibility" % self.scale, l=True)

        for axis in ["X", "Y", "Z"]:
            cmds.connectAttr("%s.guideScale" % self.node, "%s.scale%s" % (self.scale, axis))

        for axis in ["X", "Y", "Z"]:
            cmds.setAttr("%s.jointOrient%s" % (self.node, axis), k=False)
            cmds.setAttr("%s.jointOrient%s" % (self.node, axis), l=True)

            cmds.setAttr("%s.rotate%s" % (self.node, axis), k=False)
            cmds.setAttr("%s.rotate%s" % (self.node, axis), l=True)

            cmds.setAttr("%s.scale%s" % (self.node, axis), k=False)
            cmds.setAttr("%s.scale%s" % (self.node, axis), l=True)

        cmds.setAttr("%s.visibility" % self.node, k=False)
        cmds.setAttr("%s.visibility" % self.node, l=True)

        # Create main aim transform
        self.aim = cmds.group(name=libName.update(self.node, suffix="aim"), empty=True)
        cmds.connectAttr("%s.debug" % self.node, "%s.displayLocalAxis" % self.aim)

        cmds.setAttr('%s.translateZ' % self.aim, -0.00000001)

        self.__nodes["setup"] = self.setup
        self.__nodes["scale"] = self.scale
        self.__nodes["aim"] = self.aim
        self.__nodes["node"] = self.node
        self.__nodes["shapes"] = self.shapes

        # Tidy up
        cmds.parent([self.aim], self.setup)
        self.__trash.extend([_sphere])

    def __create_up(self):
        """
        """

        self.up = Up(self).create()

        _up_conds = []
        for axis_index, axis in enumerate(self.AIM_ORIENT):

            # Up axis 
            up = axis[1]

            up_pma = libName.update(self.node, suffix="pma", append="upAxis%s" % up.upper())
            if not cmds.objExists(up_pma):
                up_pma = cmds.createNode("plusMinusAverage", name=up_pma)
                cmds.connectAttr("%s.output1D" % up_pma, "%s.visibility" % self.up.get_shape(up))

            up_name = libName.update(self.node, suffix="cond", append="%sUp%s" % (0, up.upper()))
            up_cond = cmds.createNode("condition", name=up_name)
            _up_conds.append(up_cond)

            cmds.connectAttr("%s.aimOrient" % self.node, "%s.firstTerm" % up_cond)
            cmds.setAttr("%s.secondTerm" % up_cond, axis_index)
            cmds.setAttr("%s.colorIfTrueR" % up_cond, 1)
            cmds.setAttr("%s.colorIfFalseR" % up_cond, 0)

            cmds.connectAttr("%s.outColorR" % up_cond, "%s.input1D[%s]" % (up_pma, axis_index))

        for cond in _up_conds:
            cmds.connectAttr("%s.aimAt" % self.node, "%s.colorIfTrueR" % cond)

    def __create_aim(self):
        """
        """

        # Create local orient
        self.orient = cmds.orientConstraint(self.node, self.setup, mo=True)[0]
        aliases = cmds.orientConstraint(self.orient, q=True, wal=True)
        targets = cmds.orientConstraint(self.orient, q=True, tl=True)
        index = targets.index(self.node)
        condition = cmds.createNode("condition",
                                    name=libName.update(self.node, suffix="cond", append="local"))

        cmds.setAttr('%s.secondTerm' % condition, index)
        cmds.setAttr('%s.colorIfTrueR' % condition, 1)
        cmds.setAttr('%s.colorIfFalseR' % condition, 0)
        cmds.connectAttr('%s.outColorR' % condition, '%s.%s' % (self.orient, aliases[index]))

        # Create main aim constraint
        self.constraint = cmds.aimConstraint(self.node,
                                             self.aim,
                                             worldUpObject=self.up.node,
                                             offset=(0, 0, 0),
                                             aimVector=(1, 0, 0),
                                             upVector=(0, 1, 0),
                                             worldUpType='object')[0]
        aim_aliases = cmds.aimConstraint(self.constraint, q=True, wal=True)
        cmds.connectAttr('%s.outColorR' % condition, '%s.%s' % (self.constraint, aim_aliases[0]))

        # Create custom aim constraint offsets
        aim_offset_pma = cmds.createNode("plusMinusAverage",
                                        name=libName.update(self.node, suffix="pma", append="custom"))

        cmds.connectAttr("%s.output3D" % aim_offset_pma, "%s.offset" % self.constraint)

        for pair_index, axis in enumerate(self.AIM_ORIENT.keys()):

            primary, secondary = self.AIM_ORIENT[axis]

            # Axis condition
            pair_cond = cmds.createNode("condition",
                                        name=libName.update(self.node,
                                                            append="aim%s" % pair_index,
                                                            suffix="cond"))

            cmds.connectAttr("%s.aimOrient" % self.node, "%s.firstTerm" % pair_cond)
            cmds.setAttr("%s.secondTerm" % pair_cond, pair_index)
            cmds.setAttr("%s.colorIfFalse" % pair_cond, *(0, 0, 0), type="float3")
            cmds.connectAttr("%s.outColor" % pair_cond, "%s.input3D[%s]" % (aim_offset_pma, pair_index))

            # Flip condition
            flip_cond = cmds.createNode("condition",
                                        name=libName.update(self.node,
                                                            append="aim%sFlip" % pair_index,
                                                            suffix="cond"))
            cmds.connectAttr("%s.aimFlip" % self.node, "%s.firstTerm" % flip_cond)
            cmds.setAttr("%s.secondTerm" % flip_cond, 1)

            cmds.setAttr("%s.colorIfTrue" % flip_cond, *secondary, type="float3")
            cmds.setAttr("%s.colorIfFalse" % flip_cond, *primary, type="float3")
            cmds.connectAttr("%s.outColor" % flip_cond, "%s.colorIfTrue" % pair_cond)

        self.__nondag.append(condition)
        self.__nodes["constraint"] = self.constraint

    def __create_shader(self):

        self.shader, self.sg = libShader.get_or_create_shader("C_guide_0_shd", 'lambert')
        cmds.sets(self.shapes, edit=True, forceElement=self.sg)

        self.__nodes["shader"] = self.shader
        self.__nodes["sg"] = self.sg

        rgb = (1, 1, 0)
        cmds.setAttr('%s.color' % self.shader, *rgb, type='float3')
        cmds.setAttr('%s.incandescence' % self.shader, *rgb, type='float3')
        cmds.setAttr('%s.diffuse' % self.shader, 0)

    def __post(self):
        """
        Post node creation
        """

        # Clean up trash
        cmds.delete(self.__trash)

        # Burn in nodes
        cmds.setAttr("%s.nodes" % self.node, json.dumps(self.__nodes), type="string")
        cmds.setAttr("%s.nondag" % self.node, json.dumps(self.__nondag), type="string")
