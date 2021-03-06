#!/usr/bin/env python

"""
A guide model used to represent a joint in Maya and includes
some extra functionality for simple aim manipulation and control.
"""

import time
import json
import logging
from maya import cmds

from collections import OrderedDict
from crefor.lib import libName, libAttr
from crefor.model import Node
from crefor.model.shader import Shader

logger = logging.getLogger(__name__)

__all__ = ["Guide"]

class Guide(Node):
    """
    A guide model is a represetionation of a joint
    in Maya that includes some extra functionality.

    :param      position:           L, R, C, etc
    :type       position:           str
    :param      description:        Description of guide
    :type       description:        str
    :param      index:              Index of guide
    :type       index:              int
    :returns:                       Guide object
    :rtype:                         Guide

    **Example**:

    >>> Guide("C", "spine", index=0)
    # Result: <Guide 'C_spine_0_gde'> #
    """

    SUFFIX = 'gde'
    DEFAULT_AIMS = ["world", "custom"]

    _RADIUS = 1.0
    _TRANSPARENCY = 0.6

    AIM_ORIENT = OrderedDict([
                             ("xyz", [(0, 0, 0), (0, 180, 0)]),
                             ("xzy", [(-90, 0, 0), (-90, 180, 0)]),
                             ("yxz", [(0, -180, -90), (0, 0, 90)]),
                             ("yzx", [(0, -90, -90), (180, 90, -90)]),
                             ("zxy", [(-90, 180, -90), (90, 180, -90)]),
                             ("zyx", [(-90, 90, -90), (-90, -90, 90)])
                             ])

    @classmethod
    def validate(cls, node):
        """validate(guide)

        Confirm the input node is a guide.

        :param      node:       Maya node to validate
        :type       node:       Guide, str
        :returns:               Initialised guide
        :rtype:                 Guide
        :raises:                TypeError, NameError

        **Example**:

        >>> Guide.validate("C_spine_0_gde")
        # Result: <Guide 'C_spine_0_gde'> #
        """

        try:

            if not str(node).endswith(cls.SUFFIX):
                raise NameError()

            if isinstance(node, cls):
                return node
            else:
                return cls(*libName.decompile(str(node), 3)).reinit()

        except Exception:
            msg = "'%s' is not a valid guide." % node
            logger.error(msg)
            raise TypeError(msg)

    def __init__(self, position, description, index=0):
        super(Guide, self).__init__(position, description, index)

        # Constraint utils
        self.up = None
        self.aim = None

        # Snapshot
        self.__nodes = {}
        self.__nondag = []

        # Other
        self.__trash = []

    def create(self):
        """
        Create a guide node.

        :returns:       Guide model
        :rtype:         Guide
        :raises:        RuntimeError

        **Example**:

        >>> root = Guide("C", "root", 0)
        # Result: <Guide 'C_root_0_gde'> #
        """

        if self.exists():
            msg = "Cannot create guide '%s', Maya node already exists: <type '%s'>" % (self.node, cmds.nodeType(self.node))
            logger.error(msg)
            raise RuntimeError(msg)

        t = time.time()

        self.__create_nodes()
        self.__create_up()
        self.__initialise_aim()
        self.__create_shader()
        self.__post()

        logger.info("Guide created: '%s' (%0.3fs)" % (self.node,
                                                     time.time()-t))

        return self

    def reinit(self):
        """
        Reinitialise an existing guide. The guide must exist in the
        Maya scene otherwise a RuntimeError exception is raised.

        :returns:       Guide model
        :rtype:         Guide
        :raises:        RuntimeError

        **Example**:

        >>> root = Guide("C", "root", 0)
        >>> root.create()
        >>> root.reinit()
        # Result: <Guide 'C_root_0_gde'> #
        """

        if not self.exists():
            raise RuntimeError("Cannot reinit '%s' as guide does not exist." % self.node)

        # Shaders
        shader_data = json.loads(cmds.getAttr("%s.shaders" % self.node))
        self.shader = Shader(*libName.decompile(shader_data["node"], 3),
                             shader=shader_data["type"]).reinit()

        # Get setup node
        for key, item in self.nodes.items():
            setattr(self, key, item)

        self.up = Up(self).reinit()

        # Get snapshot
        self.__nodes = json.loads(cmds.getAttr("%s.nodes" % self.node))
        self.__nondag = json.loads(cmds.getAttr("%s.nondag" % self.node))

        return self

    def duplicate(self):
        """
        Create a new guide from this guide. The duplicate guide index
        will be the nearest positive unused integer.

        :returns:       Guide model
        :rtype:         Guide
        :raises:        RuntimeError

        **Example**:

        >>> root = Guide("C", "root", 0)
        >>> root.create()
        >>> root.duplicate()
        # Result: <Guide 'C_root_1_gde'> #
        """

        if not self.exists():
            raise RuntimeError("Cannot duplicate guide '%s' as it does not exist." % self.node)

        name = libName.generate(self.node)
        return Guide(*libName.decompile(name, 3)).create()

    def remove(self):
        """
        Remove the guide from the Maya scene. This also automatically
        detached itself from any children or parent guides.

        **Example**:

        >>> root = Guide("C", "root", 0)
        >>> root.create()
        >>> root.remove()
        >>> root.exists()
        # Result: False #
        """

        if self.exists():

            self.strip()

            self.up.remove()

            if self.nondag:
                cmds.delete(self.nondag)

            cmds.delete(self.setup)
            cmds.delete(self.node)

            self.shader.remove()

    def compile(self):
        """
        Generate a joint from guide matching the guides
        orientation, position and other necessary attributes.
        
        **Note:**
        Compiling a guide into a joint does not remove it
        from the Maya scene.

        :returns:       Compiled joint
        :rtype:         str

        **Example**:

        >>> root = Guide("C", "root", 0)
        >>> root.compile()
        # Result: "C_root_0_jnt"
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
                               position=self.get_position(worldspace=True),
                               rotationOrder=rotationOrder)

            cmds.select(cl=True)
            logger.debug("Compiled guide '%s' into joint: '%s'" % (self.node, joint))

        return joint

    # ======================================================================== #
    # Aim
    # ======================================================================== #

    def flip(self):
        """
        Flip primary aim axis to be the opposite of it's current value
        """

        if self.exists() and self.up.exists():
            self.up.flip()

    def flop(self):
        """
        Flop secondary aim axis to be the opposite of it's current value
        """

        if self.exists() and self.up.exists():
            self.up.flop()

    # ======================================================================== #
    # Properties
    # ======================================================================== #

    @property
    def aim_cond(self):
        """
        """

        if self.exists():
            return self.nodes["__condition"]
        return None

    @property
    def constraint(self):
        """
        """

        if self.exists():
            return self.nodes["__constraint"]
        return None

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
        Maya formatted short name of guide node.

        :returns:   Maya formatted short name
        :rtype:     str, None

        **Example:**

        >>> arm = Guide("L", "arm", 0).create()
        >>> arm.short_name
        # Restult: L_arm_0_gde #
        """

        short_name = None
        if self.exists():
            short_name = self.long_name.split("|")[-1]
        return short_name

    @property
    def long_name(self):
        """
        Maya formatted long name of guide node.

        :returns:   Maya formatted long name
        :rtype:     str, None

        **Example:**

        >>> arm = Guide("L", "arm", 0).create()
        >>> arm.long_name
        # Restult: |L_arm_0_gde #
        """

        long_name = None
        if self.exists():
            long_name = cmds.ls(self.node, long=True)[0]
        return long_name

    @property
    def parent(self):
        """
        The current parent guide if availalble

        :returns:   Parent guide node
        :rtype:     Guide

        **Example:**

        >>> wrist.set_parent(elbow)
        >>> wrist.parent
        # Result <Guide 'L_elbow_0_gde'> #
        """

        if self.exists():
            parent = cmds.listRelatives(self.node, parent=True, type="joint")
            if parent:
                return Guide.validate(parent[0])
        return None

    @property
    def children(self):
        """
        The current children guides if available.

        :returns:   List of initialised child guides
        :rtype:     list

        **Example:**

        >>> root.children
        # Result [<Guide 'L_hip_0_gde'>, <Guide 'R_hip_0_gde'>] #
        """

        children = []
        if self.exists():
            children = cmds.listRelatives(self.node, children=True, type="joint") or []
        return map(Guide.validate, children)

    @property
    def connectors(self):
        """
        Connectors are in sync with children guides. This will return connector
        objects for valid children.

        :returns:   List of initialised connector models
        :rtype:     list

        **Example:**

        >>> root.connectors
        # Result [<Connector 'L_hip_0_cnc'>, <Connector 'R_hip_0_cnc'>] #
        """

        connectors = []
        if self.exists():
            for child in self.children:
                connectors.append(Connector(self, child).reinit())
        return connectors

    @property
    def primary(self):
        """
        The guides current primary aim axis

        :returns:   Current primary aim axis
        :rtype:     str, None

        **Example:**

        >>> root.set_axis(primary="z", secondary="y")
        >>> root.primary
        # Result: x #
        """

        if self.exists():
            order = self.AIM_ORIENT.keys()
            return order[cmds.getAttr("%s.aimOrient" % self.node)][0]
        return None

    @property
    def secondary(self):
        """
        The guides current secondary aim axis

        :returns:   Current secondary aim axis
        :rtype:     str, None

        **Example:**

        >>> root.set_axis(primary="z", secondary="y")
        >>> root.secondary
        # Result: y #
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
        Set primary and secondary aim axis for guide. Recognised axis
        are either 'x', 'y' or 'z'. You cannot set the prmiary and secondary
        axis to be the same.

        :param      primary:            Primary aim axis
        :type       primary:            str
        :param      secondary:          Secondary aim axis
        :type       secondary:          str
        :raises:                        ValueError

        **Example:**

        >>> arm.set_axis("x", "z")
        >>> arm.primary
        # Result: x #
        >>> arm.secondary
        # Result: z #
        """

        if self.exists():

            if len(set(map(str, [primary, secondary]))) == 1:
                msg = ("Cannot set both primary and secondary " \
                       "as the same axis: '%s', '%s'" % (primary, secondary))
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

    def aim_at(self, guide, add=False):
        """
        Aim at input guide if it is a child. If not, then use the
        add boolean argument to create as a child and aim at it.

        :param      guide:              Child guide to aim at. Also accepts
                                        any default aim variables found in
                                        Guide.DEFAULT_AIMS
        :type       guide:              str, Guide
        :param      add:                Add this guide and aim at it if it's not
                                        an existing child
        :type       add:                boolean
        :raises:                        RuntimeError

        **Example:**

        >>> arm.aim_at("world")
        >>> arm.aim_at("C_wrist_0_gde")
        >>> arm.aim_at("C_nonExistantGuide_0_gde")
        # RuntimeError: Guide 'C_nonExistantGuide_0_gde' is not a child of 'L_arm_0_gde' # 
        """

        if self.exists():

            enums = cmds.attributeQuery("aimAt", node=self.node, listEnum=True)[0].split(":")

            # Get world, local keywords first
            if guide in self.DEFAULT_AIMS:
                libAttr.set(self.node, "aimAt", enums.index(guide))
                return

            # Try validate guide
            try:
                guide = Guide.validate(guide)
            except Exception:
                msg = "Cannot aim '%s' at '%s', node does not exist." % (self, guide)
                logger.error(msg)
                raise RuntimeError(msg)

            # Aim guide at child, or create and aim
            if not self.has_child(guide):
                if add:
                    self.add_child(guide)
                else:
                    raise RuntimeError("Guide '%s' is not a child of '%s'" % (guide.node, self.node))

            enums = cmds.attributeQuery("aimAt", node=self.node, listEnum=True)[0].split(":")
            cmds.setAttr("%s.aimAt" % self.node, enums.index(guide.node))

    def set_position(self, x, y, z, worldspace=False):
        """
        Set position of guide in either world or local space

        :param      x:                  Position of x axis
        :type       x:                  int, float
        :param      y:                  Position of y axis
        :type       y:                  int, float
        :param      z:                  Position of z axis
        :type       z:                  int, float
        :param      worldspace:         Apply in worldspace
        :type       worldspace:         tuple, list

        **Example:**

        >>> arm.set_position(0, 3, 0, worldspace=False)
        >>> arm.set_position(12, 3.32, 11.2, worldspace=True)
        """

        if self.exists():
            logger.debug("Setting '%s' position: %s" % (self.node, [x, y, z]))
            cmds.xform(self.node, ws=worldspace, t=[x, y, z])

    def aim_flip(self, flip):
        """
        """

        if self.exists():
            libAttr.set(self.node, "aimFlip", bool(flip))

    def set_debug(self, debug):
        """
        Set debug visibility of guide. This displays localRotation axis

        :param      debug:          Display local rotation axis
        :type       debug:          bool

        **Example:**
        >>> arm.set_debug(True)
        """

        if self.exists():
            libAttr.set(self.node, "debug", bool(debug))

    def set_offset(self, x, y, z):
        """
        Offset the orient by input values

        :param      x:          Orient of x axis
        :type       x:          int, float
        :param      y:          Orient of y axis
        :type       y:          int, float
        :param      z:          Orient of z axis
        :type       z:          int, float

        **Example:**

        >>> arm.set_offset(0, 90, 0)
        """

        if self.exists():
            for axis, value in zip(["X", "Y", "Z"], [x, y, z]):
                libAttr.set(self.node, "offsetOrient%s" % axis, float(value))

    # ======================================================================== #
    # Getters
    # ======================================================================== #

    def get_position(self, worldspace=False):
        """
        Get the position of the guide node. Default values returned
        are in local space, with the option of returning in worldspace.

        :param      worldspace:         Worldspace
        :type       worldspace:         boolean
        :returns:                       Position of guide node
        :rtype:                         tuple

        **Example:**

        >>> arm.get_position(worldspace=False)
        # Result: (0, 4.0, 1.2) #
        """

        position = []
        if self.exists():
            position = cmds.xform(self.node, q=True, ws=worldspace, t=True)
        return tuple(position)

    def get_up_position(self, worldspace=False):
        """
        Get the position of the up node. Default values returned
        are in local space, with the option of returning in
        worldspace.

        :param      worldspace:         Worldspace
        :type       worldspace:         boolean
        :returns:                       Position of up node
        :rtype:                         tuple

        **Example:**

        >>> arm.get_up_position(worldspace=False)
        # Result: (0, 4.0, 1.2) #
        """

        position = []
        if self.exists():
            position = self.up.get_position(worldspace=worldspace)
        return tuple(position)

    def get_aim_at(self):
        """
        Get object that the guide is aiming at. This can either be
        a Guide node, or one of the values found in Guide.DEFAULT_AIMS.

        :returns:                       Object that guide i saiming at
        :rtype:                         Guide, None

        **Example:**

        >>> root.get_aim_at():
        # Result: world #
        """

        aim = None
        if self.exists():
            enums = cmds.attributeQuery("aimAt", node=self.node, listEnum=True)[0].split(":")
            aim = enums[cmds.getAttr("%s.aimAt" % self.node)]

            # Create guide object if valid
            if aim not in self.DEFAULT_AIMS:
                return self.validate(aim)

        return aim

    def get_offset_orient(self):
        """
        Get the offset orient of the guide node.

        :returns:                       Offset orient values
        :rtype:                         tuple

        **Example:**

        >>> root.get_offset_orient()
        # Result: (0.0, 0.0, 0.0)
        """

        values = []
        if self.exists():
            attrs = ["%s.%s" % (self.node, attr) for attr in ["offsetOrientX",
                                                              "offsetOrientY",
                                                              "offsetOrientZ"]]
            values = map(cmds.getAttr, attrs)
        return tuple(values)

    def get_child(self, guide):
        """
        Get the input child guide if it is a child guide.

        :param      guide:          Guide
        :type       guide:          Guide, str
        :returns:                   Child guide
        :rtype:                     Guide

        **Example:**
        >>> root.get_child("L_hip_0_gde")
        # Result <Guide 'L_hip_0_gde'> #
        """

        guide = Guide.validate(guide)
        try:
            return self.children.index(guide.node)

        except Exception:
            msg = "Guide '%s' is not a child of: '%s'" % (guide.node, self.node)
            logger.error(msg)
            raise ValueError(msg)

    def snapshot(self):
        """
        Create a data snapshot of the guide

        :returns:           Dictionary of relevant guide information
        :rtype:             dict

        **Example**:

        >>> root = Guide("C", "root", 0)
        >>> root.create()
        >>> root.snapshot()
        # Result: {'node': u'C_root_0_gde', '...': '...'}
        """

        return dict(node=self.node,
                    parent=self.parent.node if self.parent else None,
                    children=map(str, self.children),
                    offset=self.get_offset_orient(),
                    aim_at=self.get_aim_at(),
                    aim_flip=bool(cmds.getAttr("%s.aimFlip" % self.node)),
                    position=self.get_position(worldspace=True),
                    up_position=self.get_up_position(worldspace=True),
                    primary=self.primary,
                    secondary=self.secondary) if self.exists() else {}

    # ======================================================================== #
    # Public
    # ======================================================================== #

    def strip(self):
        """
        Remove guide from any hierarchy. This unparents itself
        from any children and removes itself as a child of any
        nodes.

        **Example:**

        >>> root.strip()
        >>> root.parent
        # Result: None #
        >>> root.children
        # Result: [] #
        """

        if self.exists():

            if self.parent:
                self.remove_parent()

            children = self.children
            if children:
                for child in children:
                    self.remove_child(child)

    def has_child(self, guide):
        """
        Is input guide an immediate child of this guide?

        :param      guide:          Guide
        :type       guide:          Guide, str
        :returns:                   If the guide is a child
        :rtype:                     boolean

        **Example:**

        >>> root.has_child("L_hip_0_gde")
        # Result: True #
        """

        guide = self.validate(guide)
        has_child = False
        if self.exists():
            has_child = guide in self.children
        return has_child

    def is_parent(self, guide):
        """
        Is input guide the immediate parent of this guide?

        :param      guide:          Guide
        :type       guide:          Guide, str
        :returns:                   If the guide is the parent
        :rtype:                     boolean

        **Example:**

        >>> wrist.is_parent("L_elbow_0_gde")
        # Result: True #
        """

        guide = self.validate(guide)
        is_parent = False
        if self.exists():
            is_parent = guide == self.parent
        return is_parent

    def has_parent(self, guide):
        """
        Is the input guide a parent of this guide? This method
        reads through all parent guides hierarchy to determine
        it's return result.

        :param      guide:          Guide
        :type       guide:          Guide, str
        :returns:                   If the guide has the parent
        :rtype:                     boolean

        **Example:**

        >>> toe.has_parent("C_root_0_gde")
        # Result: True #
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
        Set this guides parent to be the input guide.

        :param      guide:          Guide
        :type       guide:          Guide, str
        :returns:                   Child guide
        :rtype:                     Guide

        **Example:**

        >>> elbow = Guide("L", "elbow", 0).create()
        >>> wrist = Guide("L", "wrist", 0).create()
        >>> wrist.set_parent("L_elbow_0_gde")
        # Result: <Guide 'L_wrist_0_gde'> #
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
        Add input guide as a child to this guide.

        :param      guide:          Guide
        :type       guide:          Guide, str
        :returns:                   Child guide
        :rtype:                     Guide

        **Example:**

        >>> elbow = Guide("L", "elbow", 0).create()
        >>> wrist = Guide("L", "wrist", 0).create()
        >>> elbow.add_child(wrist)
        # Result: <Guide 'L_wrist_0_gde'> #
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
        Remove guides immediate parent.

        **Example:**

        >>> wrist = Guide("L", "wrist", 0).create()
        >>> wrist.remove_parent()
        >>> wrist.parent
        # Result: None #
        """

        if self.exists():
            if self.parent:
                self.parent.__remove_aim(self)

    def remove_child(self, guide):
        """
        Remove input guide as a child.

        :param      guide:          Guide
        :type       guide:          Guide, str
        :returns:                   Child guide
        :rtype:                     Guide
        :raises                     ValueError

        **Example:**

        >>> elbow.remove_child(wrist)
        """

        if self.exists():
            self.__remove_aim(guide)

    # ======================================================================== #
    # Private
    # ======================================================================== #

    def __add_aim(self, guide):
        """
        Private aim creation method. Add the input guide as a child
        by extending this guides aimConstraint values and adding
        an aim enum value to the 'aimAt' attribute.
        """

        cmds.aimConstraint(guide.aim, self.aim, worldUpObject=self.up.node,
                           worldUpType='object',
                           aimVector=(1, 0, 0),
                           upVector=(0, 1, 0),
                           mo=False)

        # Edit aim attribute on node to include new child
        enums = cmds.attributeQuery('aimAt', node=self.node, listEnum=True)[0].split(':')
        enums.append(guide.node)
        libAttr.edit_enum(self.node, "aimAt", enums=enums)

        # Create connector
        con = Connector(self, guide)
        con.create()

        # Parent new guide under self
        cmds.parent(guide.node, self.node, a=True)

        return guide

    def __remove_aim(self, guide):
        """
        Remove input guide as a child guide.
        """

        t = time.time()

        if not self.has_child(guide):
            raise ValueError("Guide '%s' is not a child of '%s'" % (guide.node, self.node))

        # Remove connector
        connectors = self.connectors
        for con in connectors:
            if con.parent == self:
                con.remove()
                connectors.remove(con)
                break

        # Parent guide to world
        cmds.parent(guide.node, world=True)

        # Remove enum name
        enums = cmds.attributeQuery("aimAt", node=self.node, listEnum=True)[0].split(":")
        enums.remove(guide.node)
        libAttr.edit_enum(self.node, "aimAt", enums)
        libAttr.set(self.node, "aimAt", len(enums) - 1)

        aliases = cmds.aimConstraint(self.constraint, q=True, wal=True)
        for alias in aliases:
            if not cmds.listConnections("%s.%s" % (self.constraint, alias),
                                        source=True,
                                        destination=False,
                                        plugs=True):
                libAttr.set(self.constraint, alias, 0)

        # Default to world if no aim objects are attached
        if len(enums) == len(self.DEFAULT_AIMS):
            libAttr.set(self.node, "aimAt", 0)

        logger.debug("'%s' remove child: '%s' (%0.3fs)" % (self.node,
                                                           guide.node,
                                                           time.time()-t))

    def __update_aim_index(self):
        """
        As guides get added and removed, their linked enum index changes.
        This method scans the enum attributes and links their value to
        the current attached child guides.
        """

        # Query parent joint enum items
        enums = cmds.attributeQuery("aimAt", node=self.node, listEnum=True)[0].split(':')
        enum_index = enums.index(self.__child.node)

        # Update index to reflect alias index of child
        libAttr.set(self.aim_cond, "secondTerm", enum_index)

        state_conds = json.loads(cmds.getAttr("%s.states" % self.node))
        for key, cond in state_conds.items():
            libAttr.set(self.condition, "secondTerm", enum_index)

    def __create_nodes(self):
        """
        Main node creation method.

        A node is simply a Maya joint node, with a nurbs surface sphere
        shape parented under it as a child. All custom attributes are also
        created in this method.

        A setup node is a transform with all business logic nodes parented
        under it, including scale cluster and main aim transform target.
        """
        
        # Create node and parent sphere under
        cmds.select(cl=True)
        self.node = cmds.joint(name=self.node)
        libAttr.set(self.node, "radius", channelBox=False, l=True)
        cmds.select(cl=True)

        # Create attributes
        libAttr.add_double(self.node, "guideScale", min=0.01, dv=1)
        libAttr.add_enum(self.node, "aimOrient", enums=self.AIM_ORIENT.keys())
        libAttr.add_bool(self.node, "aimFlip", dv=False)
        libAttr.add_enum(self.node, "aimAt", enums=self.DEFAULT_AIMS)

        for offset_axis in ["offsetOrientX", "offsetOrientY", "offsetOrientZ"]:
            libAttr.add_double(self.node, offset_axis)

        libAttr.add_bool(self.node, "debug", dv=False)

        for key in ["nodes", "nondag", "shaders"]:
            libAttr.add_string(self.node, key)

        # Set attribute display status
        for attr in ["rotateOrder", "guideScale", "aimAt", "aimOrient", "aimFlip", "debug"]:
            libAttr.set(self.node, attr, keyable=False, channelBox=True)

        for axis in ["X", "Y", "Z"]:
            libAttr.set_keyable(self.node, "offsetOrient%s" % axis)

        # Create shapes
        _sphere = cmds.sphere(radius=self._RADIUS, ch=False)[0]
        _shapes = cmds.listRelatives(_sphere, type="nurbsSurface", children=True)
        self.shapes = [cmds.rename(_shapes[0], "%sShape" % self.node)]
        cmds.parent(self.shapes, self.node, r=True, s=True)
        libAttr.set(self.node, "drawStyle", 2)

        # Setup node
        self.setup = cmds.group(name=libName.update(self.node, suffix="setup"), empty=True)
        cmds.pointConstraint(self.node, self.setup, mo=False)

        # Create scale cluster
        _cl, _scale = cmds.cluster(self.shapes)
        libAttr.set(_cl, "relative", True)
        self.scale = cmds.rename(_scale, libName.update(self.node, append="scale", suffix="clh"))
        cmds.parent(self.scale, self.setup)

        # Lock down scale node
        for attr in ["translate", "rotate"]:
            for axis in ["X", "Y", "Z"]:
                libAttr.set(self.scale, "%s%s" % (attr, axis), l=True)
        libAttr.set(self.scale, "visibility", 0, k=False, l=True)
        libAttr.set(self.node, "visibility", k=False, l=True)

        for axis in ["X", "Y", "Z"]:
            cmds.connectAttr("%s.guideScale" % self.node, "%s.scale%s" % (self.scale, axis))

        for attr in ["jointOrient", "rotate", "scale"]:
            for axis in ["X", "Y", "Z"]:
                libAttr.set(self.node, "%s%s" % (attr, axis), k=False, l=True)

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
        Create up object that serves as the up control for the secondary aim
        axis. This object is accessed with the 'up' property.
        """

        self.up = Up(self).create()

        up_conds = []
        for axis_index, axis in enumerate(self.AIM_ORIENT):

            up_pma = libName.update(self.node, suffix="pma", append="upAxis%s" % axis[1].upper())

            if not cmds.objExists(up_pma):
                up_pma = cmds.createNode("plusMinusAverage", name=up_pma)
                cmds.connectAttr("%s.output1D" % up_pma, "%s.visibility" % self.up.get_shape(axis[1]))

            up_name = libName.update(self.node, suffix="cond", append="Up%s" % ("".join(axis).title()))
            up_cond = cmds.createNode("condition", name=up_name)
            up_conds.append(up_cond)

            cmds.connectAttr("%s.aimOrient" % self.node, "%s.firstTerm" % up_cond)
            libAttr.set(up_cond, "secondTerm", axis_index)
            libAttr.set(up_cond, "colorIfTrueR", 1)
            libAttr.set(up_cond, "colorIfFalseR", 0)

            cmds.connectAttr("%s.outColorR" % up_cond, "%s.input1D[%s]" % (up_pma, axis_index))

        for cond in up_conds:
            cmds.connectAttr("%s.aimAt" % self.node, "%s.colorIfTrueR" % cond)

    def __initialise_aim(self):
        """
        Create inital aim logic network. This is where the guides main
        aim constraint is made and initialised
        """

        # Make main aim_cond
        self.__condition = cmds.createNode("condition",
                                        name=libName.update(self.node,
                                                            suffix="cond",
                                                            append="local"))

        # Create local orient
        orient_constraint = cmds.orientConstraint(self.node, self.setup, mo=True)[0]
        aliases = cmds.orientConstraint(orient_constraint, q=True, wal=True)
        targets = cmds.orientConstraint(orient_constraint, q=True, tl=True)
        index = targets.index(self.node)

        libAttr.set(self.__condition, "secondTerm", index)
        libAttr.set(self.__condition, "colorIfTrueR", 1)
        libAttr.set(self.__condition, "colorIfFalseR", 0)
        cmds.connectAttr("%s.outColorR" % self.__condition, "%s.%s" % (orient_constraint, aliases[index]))

        # Create main aim constraint
        self.__constraint = cmds.aimConstraint(self.node,
                                             self.aim,
                                             worldUpObject=self.up.node,
                                             offset=(0, 0, 0),
                                             aimVector=(1, 0, 0),
                                             upVector=(0, 1, 0),
                                             worldUpType='object')[0]
        aim_aliases = cmds.aimConstraint(self.__constraint, q=True, wal=True)
        cmds.connectAttr('%s.outColorR' % self.__condition, '%s.%s' % (self.__constraint, aim_aliases[0]))

        # Create custom aim constraint offsets
        aim_offset_pma = cmds.createNode("plusMinusAverage",
                                        name=libName.update(self.node, suffix="pma", append="custom"))

        cmds.connectAttr("%s.output3D" % aim_offset_pma, "%s.offset" % self.__constraint)

        for pair_index, axis in enumerate(self.AIM_ORIENT.keys()):

            primary, secondary = self.AIM_ORIENT[axis]

            # Axis condition
            pair_cond = cmds.createNode("condition",
                                        name=libName.update(self.node,
                                                            append="aim%s" % pair_index,
                                                            suffix="cond"))

            cmds.connectAttr("%s.aimOrient" % self.node, "%s.firstTerm" % pair_cond)
            cmds.connectAttr("%s.outColor" % pair_cond, "%s.input3D[%s]" % (aim_offset_pma, pair_index))

            libAttr.set(pair_cond, "secondTerm", pair_index)
            libAttr.set(pair_cond, "colorIfFalse", *(0, 0, 0), type="float3")

            # Flip condition
            flip_cond = cmds.createNode("condition",
                                        name=libName.update(self.node,
                                                            append="aim%sFlip" % pair_index,
                                                            suffix="cond"))
            cmds.connectAttr("%s.aimFlip" % self.node, "%s.firstTerm" % flip_cond)
            cmds.connectAttr("%s.outColor" % flip_cond, "%s.colorIfTrue" % pair_cond)

            libAttr.set(flip_cond, "secondTerm", 1)
            libAttr.set(flip_cond, "colorIfTrue", *secondary, type="float3")
            libAttr.set(flip_cond, "colorIfFalse", *primary, type="float3")

        # Add custom orient offset
        for attr, axis in zip(["offsetOrientX", "offsetOrientY", "offsetOrientZ"], ["x", "y", "z"]):
            cmds.connectAttr("%s.%s" % (self.node, attr),
                             "%s.input3D[%s].input3D%s" % (aim_offset_pma,
                                                           (pair_index + 1),
                                                           axis))

        self.__nodes["__condition"] = self.__condition
        self.__nodes["__constraint"] = self.__constraint

    def __create_shader(self):
        """
        """

        self.shader = Shader("N", "guide", 0).create()
        self.shader.add(self.shapes)

        rgb = (1, 1, 0)
        libAttr.set(self.shader, "color", *rgb, type="float3")
        libAttr.set(self.shader, "incandescence", *rgb, type="float3")
        libAttr.set(self.shader, "diffuse", 0)
        libAttr.set(self.shader, "transparency",
                    *[self._TRANSPARENCY, self._TRANSPARENCY, self._TRANSPARENCY],
                    type="float3")

        # cmds.setAttr("%s.color" % self.shader, *rgb, type="float3")
        # cmds.setAttr("%s.incandescence" % self.shader, *rgb, type="float3")
        # cmds.setAttr("%s.diffuse" % self.shader, 0)
        # cmds.setAttr("%s.transparency" % self.shader,
        #              *[self._TRANSPARENCY, self._TRANSPARENCY, self._TRANSPARENCY],
        #              type="float3")

    def __post(self):
        """
        Post node creation
        """

        # Clean up trash
        cmds.delete(self.__trash)

        # Burn in nodes
        libAttr.set(self.node, "nodes", json.dumps(self.__nodes), type="string")
        libAttr.set(self.node, "nondag", json.dumps(self.__nondag), type="string")

        # Burn in shader data
        shader_data = {"node": self.shader.node, "type": self.shader.type}
        libAttr.set(self.node, "shaders", json.dumps(shader_data), type="string")


class Up(Node):
    """
    """

    SUFFIX = "up"

    _DEFAULT_SCALE = 0.4
    _DEFAULT_POSITION = (0, 3, 0)

    def __init__(self, guide):

        self.guide = Guide.validate(guide)

        self.__shapes = {}
        self.__nodes = {}
        self.__shaders = {}

        super(Up, self).__init__(*libName.decompile(self.guide.node, 3))

    @property
    def nodes(self):
        """nodes(self)
        Return important nodes from Guide class

        :returns:   Dictionary of important nodes in {"attr": "value"} format
        :rtype:     dict

        **Example**:

        >>> arm = Guide("L", "arm", 0).create()
        >>> up = Up(arm)
        >>> up.nodes
        # Result: {u'nodes': [u'L_armLocal_0_cond'], "...": "..."} # 
        """

        if self.exists():
            if not self.__nodes:
                self.__nodes = json.loads(cmds.getAttr("%s.nodes" % self.node))
            return self.__nodes
        return {}

    @property
    def shaders(self):
        """
        """

        if self.exists():
            if not self.__shaders:
                self.__shaders = json.loads(cmds.getAttr("%s.shaders" % self.node))
            
            shaders = []
            for axis, shader_data in self.__shaders.items():
                node = shader_data["node"]
                _type = shader_data["type"]
                shaders.append(Shader(*libName.decompile(node, 3), shader=_type).reinit())

            return shaders
        return {}

    def get_shape(self, axis):
        """
        """

        try:
            return getattr(self, axis.lower())
        except AttributeError:
            return None

    def get_position(self, worldspace=False):
        """
        """

        position = []
        if self.exists():
            position = cmds.xform(self.node, q=True, ws=worldspace, t=True)
        return tuple(position)

    def flip(self):
        """
        """

        if self.exists():

            aim_at = cmds.getAttr("%s.aimAt" % self.guide.node)
            if aim_at >= 1:
                value = cmds.getAttr("%s.translateX" % self.node) * -1
                libAttr.set(self.node, "translateX", value)
            else:
                logger.warning("Cannot flip aim when guide '%s' is set to world space" % self.guide.node)

    def flop(self):
        """
        """

        if self.exists():
            aim_at = cmds.getAttr("%s.aimAt" % self.guide.node)
            if aim_at >= 1:
                value = cmds.getAttr("%s.translateY" % self.node) * -1
                libAttr.set(self.node, "translateY", value)
            else:
                logger.warning("Cannot flop aim when guide '%s' is set to world space" % self.guide.node)

    def set_position(self, vector3f, worldspace=False):
        """
        """

        if self.exists():
            try:
                cmds.xform(self.node, ws=worldspace, t=vector3f)
            except Exception:
                logger.error("Failed to set translates on '%s' with args: '%s'" % (self.node, vector3f))

    def __create_nodes(self):
        """
        """

        self.node = cmds.group(name=self.node, empty=True)
        self.grp = cmds.group(self.node, name=libName.update(self.node, append="up", suffix="grp"))

        # Lock down rotate, scale and visibility
        for attr in ["rotate", "scale"]:
            for axis in ["X", "Y", "Z"]:
                libAttr.set(self.node, "%s%s" % (attr, axis), k=False, l=True)
        libAttr.set(self.node, "visibility", k=False, l=False)

        _x = cmds.sphere(name=libName.update(self.node, append="X", suffix="up"), radius=self._DEFAULT_SCALE)[0]
        _y = cmds.sphere(name=libName.update(self.node, append="Y", suffix="up"), radius=self._DEFAULT_SCALE)[0]
        _z = cmds.sphere(name=libName.update(self.node, append="Z", suffix="up"), radius=self._DEFAULT_SCALE)[0]

        self.x = cmds.listRelatives(_x, type="nurbsSurface")[0]
        self.y = cmds.listRelatives(_y, type="nurbsSurface")[0]
        self.z = cmds.listRelatives(_z, type="nurbsSurface")[0]

        cmds.parent([self.x, self.y, self.z], self.node, r=True, s=True)

        for axis in ["X", "Y", "Z"]:
            cmds.connectAttr("%s.guideScale" % self.guide.node, "%s.scale%s" % (self.grp, axis))

        # Tidy up
        cmds.parent(self.grp, self.guide.setup)

        cmds.delete(self.node, ch=True)
        cmds.delete([_x, _y, _z])

        self.__nodes["x"] = self.x
        self.__nodes["y"] = self.y
        self.__nodes["z"] = self.z
        self.__nodes["grp"] = self.grp

        # Add attributes
        libAttr.add_double(self.node, "guideScale", min=0.01, dv=1, k=True)

        # Create scale cluster
        _cl, _scale = cmds.cluster([self.x, self.y, self.z])
        cmds.setAttr("%s.relative" % _cl, True)
        libAttr.set(_cl, "relative", True)
        self.scale = cmds.rename(_scale, libName.update(self.node, append="upScale", suffix="clh"))
        cmds.parent(self.scale, self.node)

        for axis in ["X", "Y", "Z"]:
            cmds.connectAttr("%s.guideScale" % self.node, "%s.scale%s" % (self.scale, axis))

        # Offset node initial position
        libAttr.set(self.node,
                    "translate",
                    *self._DEFAULT_POSITION,
                    type="float3")

    def __create_shaders(self):
        """
        """

        shader_data = {"X": (1, 0, 0),
                       "Y": (0, 1, 0),
                       "Z": (0, 0, 1)}

        for axis, rgb in shader_data.items():

            shader = Shader("N", "guide%s" % axis.title(), 0).create()

            libAttr.set(shader.node, "color", *rgb, type="float3")
            libAttr.set(shader.node, "incandescence", *rgb, type="float3")
            libAttr.set(shader.node, "diffuse", 0)

            shader.add(self.get_shape(axis))

            self.__shaders[axis] = {"node": shader.node, "type": shader.type}

    def __post(self):
        """
        Post node creation
        """

        # Burn in nodes
        for key in ["nodes", "shaders"]:
            libAttr.add_string(self.node, key)

        libAttr.set(self.node, "nodes", json.dumps(self.__nodes), type="string")
        libAttr.set(self.node, "shaders", json.dumps(self.__shaders), type="string")

        # Lock down cluster
        libAttr.set(self.scale, "visibility", False)
        libAttr.lock_all(self.scale)

    def create(self):
        """
        """

        if self.exists():
            msg = "Cannot create Up model '%s', already exists with guide: '%s'" % (self.node, self.guide.node)
            logger.error(msg)
            raise RuntimeError(msg)

        self.__create_nodes()
        self.__create_shaders()

        self.__post()

        return self

    def reinit(self):
        """
        """

        for key, item in self.nodes.items():
            setattr(self, key, item)

        shaders = json.loads(cmds.getAttr("%s.shaders" % self.node))
        for axis in shaders:

            node = shaders[axis]["node"]
            _type = shaders[axis]["type"]

            self.__shaders[axis] = {"node": Shader(*libName.decompile(node, 3), shader=_type).node,
                                    "type": _type}

        # Get snapshot
        self.__nodes = json.loads(cmds.getAttr("%s.nodes" % self.node))

        return self

    def remove(self):
        """
        """

        if self.exists():
            cmds.delete(self.node)

            for axis, shader_data in self.__shaders.items():
                shader = Shader(*libName.decompile(shader_data["node"], 3)).reinit()
                shader.remove()


class Connector(Node):
    """
    A connector model is used to create a connection between
    two guide models. This includes a annotation pointing between
    both guides and a new condition which determines if the parent
    guide 'aims' at the child guide when the parent aim enum attribute
    is matched to the childs name.

    :param      parent:             Parent guide
    :type       parent:             Guide
    :param      parent:             Child guide
    :type       parent:             Guide
    :returns:                       Connector object
    :rtype:                         Connector

    **Example**:

    >>> Connector("C_spine_0_gde", "L_arm_0_gde")
    # Result: <Connector 'L_arm_0_gde'> #
    """

    SUFFIX = 'cnc'

    def __init__(self, parent, child):

        # Guides
        self.__parent = Guide.validate(parent)
        self.__child = Guide.validate(child)

        # Collection of nodes for reinit
        self.__nodes = {}

        super(Connector, self).__init__(*libName.decompile(self.child.node, 3))

    @property
    def parent(self):
        """parent()
        Return connectors parent guide

        :returns:   Parent guide
        :rtype:     Guide

        **Example**:

        >>> con = spine.connectors[0]
        >>> con.parent
        # Result: <Guide 'C_spine_0_gde'> #
        """

        return self.__parent

    @property
    def child(self):
        """child()
        Return connectors child guide

        :returns:   Child guide
        :rtype:     Guide

        **Example**:

        >>> con = spine.connectors[0]
        >>> con.child
        # Result: <Guide 'L_arm_0_gde'> #
        """

        return self.__child

    @property
    def condition(self):
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
            return self.nodes["__condition"]
        return None

    @property
    def nodes(self):
        """nodes()
        Return important nodes from connector object

        :returns:   Dictionary of important nodes in {"attr": "value"} format
        :rtype:     dict

        **Example**:

        >>> con = spine.connectors[0]
        >>> con.nodes
        # Result: {} #
        """

        if self.exists():
            if not self.__nodes:
                self.__nodes = json.loads(cmds.getAttr("%s.nodes" % self.node))
            return self.__nodes
        return {}

    def __create_nodes(self):
        """
        """

        # Create annotation
        self.node = cmds.createNode("annotationShape", name=self.node)
        libAttr.set(self.node, "overrideEnabled", True)
        libAttr.set(self.node, "overrideColor", 18)
        libAttr.set(self.node, "displayArrow", False)

        # Attributes for reinit
        libAttr.add_string(self.node, "nodes")

        transform = cmds.listRelatives(self.node, parent=True)[0]

        cmds.parent(self.node, self.parent.node, shape=True, relative=True)
        cmds.delete(transform)

        libAttr.set(self.node, "displayArrow", True)
        cmds.connectAttr("%s.worldMatrix[0]" % self.child.shapes[0],
                         "%s.dagObjectMatrix[0]" % self.node,
                         force=True)

    def __create_aim(self):
        """
        """

        # Query aliases and target list from parent aim constraint
        aliases = cmds.aimConstraint(self.parent.constraint, q=True, wal=True)
        targets = cmds.aimConstraint(self.parent.constraint, q=True, tl=True)
        index = targets.index(self.child.aim)

        # Query parent joint enum items
        enums = cmds.attributeQuery("aimAt", node=self.parent.node, listEnum=True)[0].split(":")
        enum_index = enums.index(self.child.node)

        # Create condition that turns on aim for child constraint if
        # enum index is set to match childs name
        self.__condition = cmds.createNode("condition",
                                   name=libName.update(self.node,
                                                       append=libName.description(self.node),
                                                       suffix="cond"))

        libAttr.set(self.__condition, "secondTerm", enum_index)
        libAttr.set(self.__condition, "colorIfTrueR", 1)
        libAttr.set(self.__condition, "colorIfFalseR", 0)

        cmds.connectAttr("%s.aimAt" % self.parent.node, "%s.firstTerm" % self.__condition)
        cmds.connectAttr("%s.outColorR" % self.__condition, "%s.%s" % (self.parent.constraint, aliases[index]))

        # Set enum to match child aim
        libAttr.set(self.parent.node, "aimAt", enum_index)

        # Loop through all aliases on and set non-connected attributes to be 0
        for alias in aliases:
            if not cmds.listConnections('%s.%s' % (self.parent.constraint, alias),
                                        source=True,
                                        destination=False,
                                        plugs=True):
                libAttr.set(self.parent.constraint, alias, 0)

        # Store new condition
        self.__nodes["__condition"] = self.__condition

    def __update_aim_index(self):
        """
        Refresh aim index of aim condition
        """

        if self.exists():

            # Query parent joint enum items
            enums = cmds.attributeQuery("aimAt", node=self.__parent.node, listEnum=True)[0].split(':')
            enum_index = enums.index(self.__child.node)

            # Update index to reflect alias index of child
            libAttr.set(self.parent.aim_cond, "secondTerm", enum_index)

    def __post(self):
        """
        """

        # Burn in nodes
        libAttr.set(self.node, "nodes", json.dumps(self.__nodes), type="string")

        # Remove selection access
        libAttr.set(self.node, "overrideEnabled", 1)
        libAttr.set(self.node, "overrideDisplayType", 1)

    def create(self):
        """create()
        Create all nodes to represent a connector object.

        :returns:   Connector object
        :rtype:     Connector

        **Example**:

        >>> con = Connector("C_spine_0_gde", "L_arm_0_gde")
        >>> con.create()
        # Result: <Connector 'L_arm_0_cnc'> #
        """

        self.__create_nodes()
        self.__create_aim()
        self.__post()

    def remove(self):
        """remove()
        Delete all connector nodes.

        **Example**:

        >>> con = 
        >>> con.create()
        # Result: <Connector 'L_arm_0_cnc'> #
        """

        cmds.delete(self.node)

    def reinit(self):
        """reinit()
        Reinitialise connector and object nodes.

        :returns:   Connector object
        :rtype:     Connector

        **Example**:

        >>> con = spine.connectors[0]
        >>> con.reinit()
        # Result: <Connector 'L_arm_0_gde'> #
        """

        if not self.exists():
            raise Exception('Cannot reinit \'%s\' as connector does not exist.' % self.node)

        self.__nodes = json.loads(cmds.getAttr("%s.nodes" % self.node) or "{}")

        # Get setup node:
        for key, item in self.nodes.items():
            setattr(self, key, item)

        # Refresh aim index
        self.__update_aim_index()

        return self
