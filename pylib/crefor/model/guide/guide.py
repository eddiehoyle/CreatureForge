#!/usr/bin/env python

"""
"""

import json
from maya import cmds
from copy import deepcopy

from collections import OrderedDict
from crefor.lib import libName, libShader, libXform
from crefor.model import Node
from crefor.model.guide.connector import Connector

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)

__all__ = ["Guide"]

class Guide(object):
    """
    Singleton
    """

    SEP = "_"

    def __new__(self, *args, **kwargs):

        if len(args) == 3 or len(kwargs.keys()) == 3:
            return _Guide(*args, **kwargs)
        elif len(args) == 1:
            return _Guide(*str(args[0]).split(self.SEP)[:3])
        else:
            raise ValueError(args)

class _Guide(Node):

    SUFFIX = 'gde'
    RADIUS = 1.0
    DEFAULT_AIMS = ['world', 'local']
    UP_SCALE_VALUE = RADIUS/3.3

    AIM_ORDER = OrderedDict([("xyz", (0, 0, 0)),
                             ("xzy", (-90, 0, 0)),
                             ("yxz", (0, -180, -90)),
                             ("yzx", (0, -90, -90)),
                             ("zxy", (-90, 180, -90)),
                             ("zyx", (-90, 90, -90))])

    def __init__(self, position, description, index=0):
        super(_Guide, self).__init__(position, description, index)

        self.joint = None

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

        self.__burn_nodes = {}
        self.__burn_nondag = []
        self.__nondag_nodes = {}

    @property
    def nodes(self):
        """nodes(self)
        Return important nodes from Guide class

        :returns:   Dictionary of important nodes in {"attr": "value"} format
        :rtype:     dict

        **Example**:

        >>> arm = Guide("L", "arm", 0).create()
        >>> arm.nodes
        # Result: {u'nondag': [u'L_armLocal_0_cond'], "...": "..."} # 
        """

        return json.loads(cmds.getAttr("%s.snapshotNodes" % self.setup_node)) if self.exists() else {}

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

        return json.loads(cmds.getAttr("%s.snapshotNondag" % self.setup_node)) if self.exists() else {}

    @property
    def setup_node(self):
        # return libName.set_suffix(libName.append_description(self.name, "gde"), "setup")
        return self.name.recompile(suffix="setup", append=self.SUFFIX)

    @property
    def short_name(self):
        '''Short name of guide'''
        if self.exists():
            return cmds.ls(self.joint, long=True)[0].split('|')[-1]
        return None

    @property
    def long_name(self):
        '''Long name of guide'''
        if self.exists():
            return cmds.ls(self.joint, long=True)[0]
        return None

    @property
    def parent(self):
        '''Get parent joint and return guide object'''
        _parent = cmds.listRelatives(self.joint, parent=True, type='joint') if self.exists() else None
        if _parent:
            return Guide(*libName._decompile(_parent[0])[0:3]).reinit()
        return None

    @property
    def children(self):
        '''Get children joints and return dict with guide objects'''
        _children = cmds.listRelatives(self.joint, children=True, type='joint') or []
        data = {}
        for _child in _children:
            # data[_child] = Guide(*libName._decompile(_child)[0:3]).reinit()
            data[_child] = Guide(*self.name.decompile(3)).reinit()
        return data

    @property
    def connectors(self):
        '''Connectors are stored in sync with children'''
        data = {}
        for _child in self.children.values():
            data[_child.name] = Connector(self, _child).reinit()
        return data

    def set_axis(self, axis):
        """
        """

        if self.exists():
            try:
                cmds.setAttr("%s.aimOrder" % self.joint, self.AIM_ORDER.keys().index(axis))
            except Exception as e:
                e.args = ["Axis '%s' is not a valid aim axis: %s" % (axis, self.AIM_ORDER.keys())]
                raise


    def exists(self):
        '''Does the guide exist in Maya?'''
        return cmds.objExists(self.setup_node)

    def set_scale(self, value):
        '''Scale guide and related connectors'''

        selected = cmds.ls(sl=1)
        if self.joint:
            cls, clh = cmds.cluster(self.shapes)
            cmds.setAttr('%s.scale' % clh, value, value, value, type='float3')
            cmds.delete(self.shapes, ch=True)

        for con in self.connectors.values():
            con.set_start_scale(value)

        if selected:
            cmds.select(selected, r=True)

    def get_translates(self):
        """
        """

        if self.exists():
            return cmds.xform(self.joint, q=True, ws=True, t=True)
        return tuple()

    def get_axis(self):
        """
        """
        if self.exists():
            order = self.AIM_ORDER.keys()
            return order[cmds.getAttr("%s.aimOrder" % self.joint)]

    def get_aim_at(self):
        """
        """

        if self.exists():
            enums = cmds.attributeQuery('aimAt', node=self.joint, listEnum=True)[0].split(':')
            return enums[cmds.getAttr("%s.aimAt" % self.joint)]

    def aim_at(self, guide, add=False):
        """
        Aim at input guide if it is a child. If not, then use the
        add boolean argument to create as a child and aim at it.
        """

        if self.exists():
            try:

                enums = cmds.attributeQuery('aimAt', node=self.joint, listEnum=True)[0].split(':')

                if guide in ["world", "local"]:
                    cmds.setAttr("%s.aimAt" % self.joint, enums.index(guide))
                    return

                if not isinstance(guide, Guide):
                    # guide = Guide(*libName._decompile(guide)[:-1]).reinit()
                    guide = Guide(*self.name.decompile(3)).reinit()

                if not self.has_child(guide):
                    if add:
                        self.add_child(guide)
                    else:
                        raise RuntimeError("Guide '%s' is not a child of '%s'" % (guide.joint, self.joint))

                cmds.setAttr("%s.aimAt" % self.joint, enums.index(guide.aim))
            except Exception:
                raise

    def set_translates(self, vector3f):
        """
        Set position of guide
        """

        if self.joint:
            cmds.xform(self.joint, ws=True, t=vector3f)

    def set_debug(self, debug):
        '''Set debug visibility'''
        if self.joint:
            cmds.setAttr('%s.debug' % self.joint, bool(debug))

    def has_child(self, guide):
        '''Is guide an immediate child of self'''
        return guide.name in self.children

    def is_parent(self, guide):
        '''Is guide the immediate parent of self'''
        if self.parent:
            return guide.joint == self.parent.joint
        return False

    def has_parent(self, guide):
        '''Iterate over all parents to see if guide is one'''

        parent = self.parent
        while parent:
            if guide.name == parent.name:
                return True
            parent = parent.parent
        return False

    def set_parent(self, guide):
        '''Set guide to be parent of self'''

        # Try to parent to itself
        if self.name == guide.name:
            log.warning("Cannot parent '%s' to itself" % self.joint)
            return None

        # Is guide already parent
        if self.parent and self.parent.name == guide.name:
            log.debug("'%s' is already a parent of '%s'" % (guide.joint, self.joint))
            return self.parent

        # Is guide below self in hierarchy
        if guide.has_parent(self):
            guide.remove_parent()

        # If self has any parent already
        if self.parent:
            self.remove_parent()

        guide.add_aim(self)
        log.info('\'%s\' successfully set parent: \'%s\'' % (self.joint, guide.joint))

        return guide

    def add_child(self, guide):
        '''Add guide to children'''

        # Try to parent to itself
        if self.name == guide.name:
            log.warning("Cannot add '%s' to itself as child" % self.joint)
            return None

        # Guide is already a child of self
        if self.has_child(guide):
            log.info("'%s' is already a child of '%s'" % (guide.joint, self.joint))
            return self.children[guide.name]

        # If guide has any parent already
        if guide.parent:
            guide.remove_parent()

        # Is guide above self in hierarchy
        if self.has_parent(guide):
            self.remove_parent()

        self.add_aim(guide)
        log.info("'%s' successfully added child: '%s'" % (self.joint, guide.joint))
        return guide

    def add_aim(self, guide):
        '''
        Create a new child aim relationship between self and guide.
        Guide is considered to be the child of self. Any constraint
        and attribute updates are added to self, as well as the connector.
        '''

        # Already has child connector?
        connectors = deepcopy(self.connectors)
        if guide.name in connectors:
            return connectors[guide.name]

        cmds.aimConstraint(guide.aim, self.aim, worldUpObject=self.up,
                           worldUpType='object',
                           aimVector=(1, 0, 0),
                           upVector=(0, 1, 0),
                           mo=False)

        # Edit aim attribute on joint to include new child
        enums = cmds.attributeQuery('aimAt', node=self.joint, listEnum=True)[0].split(':')
        enums.append(guide.aim)
        cmds.addAttr('%s.aimAt' % self.joint, e=True, en=':'.join(enums))

        # Create connector
        con = Connector(self, guide)
        con.create()

        # Parent new guide under self
        cmds.parent(guide.joint, self.joint, a=True)

        # Reinit children
        for key, con in connectors.items():
            con.reinit()

        return guide

    def remove_parent(self):
        '''
        If have a parent, tell parent to remove aim to self
        '''

        if self.parent:
            # log.info('Removing %s parent: %s' % (self.name, self.parent.name))
            self.parent.remove_aim(self)

    def remove_child(self, guide):
        '''
        '''

        self.remove_aim(guide)

    def remove_aim(self, guide):
        '''
        self has guide as a child
        self has constraint
        self --> guide

        self is always parent
        guide is always child
        '''

        if not self.has_child(guide):
            return None

        # Remove connector
        connectors = deepcopy(self.connectors)
        if guide.name in connectors:
            connectors[guide.name].remove()
            del connectors[guide.name]

        # Parent guide to world
        cmds.parent(guide.joint, world=True)

        enums = cmds.attributeQuery('aimAt', node=self.joint, listEnum=True)[0].split(':')
        enums.remove(guide.aim)
        cmds.addAttr('%s.aimAt' % self.joint, e=True, en=':'.join(enums))
        cmds.setAttr('%s.aimAt' % self.joint, len(enums) - 1)

        aliases = cmds.aimConstraint(self.constraint, q=True, wal=True)
        for alias in aliases:
            if not cmds.listConnections('%s.%s' % (self.constraint, alias), source=True,
                                                                              destination=False,
                                                                              plugs=True):
                cmds.setAttr('%s.%s' % (self.constraint, alias), 0)

        # Default to world
        if len(enums) == 1:
            cmds.setAttr('%s.aimAt' % self.joint, 0)

        # Reinit children
        for key, con in connectors.items():
            con.reinit()

        log.info('%s remove child: %s' % (self.name, guide.name))

    def get_parent(self):
        return self.parent

    def get_child(self, name):
        return self.children.get(name, None)

    def __create_nodes(self):
        
        # Create joint and parent sphere under
        cmds.select(cl=True)
        self.joint = cmds.createNode('joint', name=self.name.compile())
        cmds.setAttr("%s.radius" % self.joint, cb=False)
        cmds.setAttr("%s.radius" % self.joint, l=True)
        cmds.select(cl=True)

        _sphere = cmds.sphere(radius=self.RADIUS, ch=False)[0]
        self.shapes = cmds.listRelatives(_sphere, type='nurbsSurface', children=True)
        cmds.parent(self.shapes, self.joint, r=True, s=True)
        cmds.setAttr('%s.drawStyle' % self.joint, 2)

        # Setup node
        cmds.group(name=self.setup_node, empty=True)
        cmds.pointConstraint(self.joint, self.setup_node, mo=False)

        # Create up transform
        # self.up = cmds.group(name=libName.set_suffix(self.name, 'up'), empty=True)
        self.up = cmds.group(name=self.name.recompile(suffix="up"), empty=True)
        _cube = cmds.nurbsCube(p=(0, 0, 0), ax=(0, 1, 0), lr=1, hr=1, d=1, u=1, v=1, ch=0)[0]
        _cube_shapes = cmds.listRelatives(_cube, type='nurbsSurface', ad=True)
        cmds.parent(_cube_shapes, self.up, r=True, s=True)
        cmds.setAttr('%s.translateY' % self.up, 2)

        # Scale up
        _clh = cmds.cluster(_cube_shapes)[1]
        cmds.setAttr('%s.scale' % _clh, 
                     self.UP_SCALE_VALUE,
                     self.UP_SCALE_VALUE,
                     self.UP_SCALE_VALUE,
                     type='float3')
        cmds.delete(self.up, ch=True)

        # Create main aim transform
        # self.aim = cmds.group(name=libName.set_suffix(self.name, 'aim'), empty=True)
        self.aim = cmds.group(name=self.name.recompile(suffix="aim"), empty=True)

        self.name.recompile(suffix="up")
        cmds.setAttr('%s.translateX' % self.aim, -0.00000001)
        

        cmds.addAttr(self.joint, ln='aimAt', at='enum', en='local')
        cmds.setAttr('%s.aimAt' % self.joint, k=False)
        cmds.setAttr('%s.aimAt' % self.joint, cb=True)

        cmds.addAttr(self.joint, ln='aimOrder', at='enum', en=":".join(self.AIM_ORDER.keys()))
        cmds.setAttr('%s.aimOrder' % self.joint, k=False)
        cmds.setAttr('%s.aimOrder' % self.joint, cb=True)

        # Tidy up
        cmds.parent([self.up, self.aim], self.setup_node)
        self.__trash.extend([_cube, _sphere])

        self.__burn_nodes["aim"] = self.aim
        self.__burn_nodes["joint"] = self.joint
        self.__burn_nodes["shapes"] = self.shapes
        self.__burn_nodes["up"] = self.up

    def __create_attribtues(self):
        """
        """

        cmds.addAttr(self.joint, ln='debug', at='bool', min=0, max=1, dv=0)
        cmds.setAttr('%s.debug' % self.joint, k=False)
        cmds.setAttr('%s.debug' % self.joint, cb=True)
        cmds.connectAttr('%s.debug' % self.joint, '%s.displayLocalAxis' % self.aim)

        for key in ["snapshotNodes", "snapshotNondag"]:
            cmds.addAttr(self.setup_node, ln=key, dt='string')
            cmds.setAttr('%s.%s' % (self.setup_node, key), k=False)

    def __create_aim(self):
        '''
        '''

        # Create local orient
        self.orient = cmds.orientConstraint(self.joint, self.setup_node, mo=True)[0]
        aliases = cmds.orientConstraint(self.orient, q=True, wal=True)
        targets = cmds.orientConstraint(self.orient, q=True, tl=True)
        index = targets.index(self.joint)
        # condition = cmds.createNode('condition',
        #                             name=libName.set_suffix(libName.append_description(self.name,
        #                                                                                'local'),
        #                                                                                'cond'))
        condition = cmds.createNode("condition",
                                    name=self.name.recompile(suffix="cond",
                                                             append="local"))


        cmds.setAttr('%s.secondTerm' % condition, index)
        cmds.setAttr('%s.colorIfTrueR' % condition, 1)
        cmds.setAttr('%s.colorIfFalseR' % condition, 0)
        cmds.connectAttr('%s.outColorR' % condition, '%s.%s' % (self.orient, aliases[index]))

        # Create main aim constraint
        self.constraint = cmds.aimConstraint(self.joint,
                                                 self.aim,
                                                 worldUpObject=self.up,
                                                 offset=(0, 0, 0),
                                                 aimVector=(1, 0, 0),
                                                 upVector=(0, 1, 0),
                                                 worldUpType='object')[0]
        aim_aliases = cmds.aimConstraint(self.constraint, q=True, wal=True)
        cmds.connectAttr('%s.outColorR' % condition, '%s.%s' % (self.constraint, aim_aliases[0]))

        # Create custom aim constraint offsets
        # aim_order_pma = cmds.createNode("plusMinusAverage",
        #                                 name=libName.set_suffix(libName.append_description(self.name,
        #                                                                                    "custom"),
        #                                                                                    "pma"))
        aim_order_pma = cmds.createNode("plusMinusAverage",
                                        name=self.name.recompile(suffix="pma",
                                                                 append="custom"))

        cmds.connectAttr("%s.output3D" % aim_order_pma, "%s.offset" % self.constraint)

        for pair_index, pair in enumerate(self.AIM_ORDER.keys()):
            # pair_cond = cmds.createNode("condition",
            #                             name=libName.set_suffix(libName.append_description(self.name,
            #                                                                                "pair%s" % pair_index),
            #                                                                                "cond"))
            pair_cond = cmds.createNode("condition",
                                        name=self.name.recompile(suffix="pair%s" % pair_index,
                                                                 append="cond"))
            cmds.connectAttr("%s.aimOrder" % self.joint, "%s.firstTerm" % pair_cond)
            cmds.setAttr("%s.secondTerm" % pair_cond, pair_index)

            cmds.setAttr("%s.colorIfTrue" % pair_cond, *self.AIM_ORDER[pair], type="float3")
            cmds.setAttr("%s.colorIfFalse" % pair_cond, *(0, 0, 0), type="float3")

            cmds.connectAttr("%s.outColor" % pair_cond, "%s.input3D[%s]" % (aim_order_pma, pair_index))

        self.__burn_nondag.append(condition)
        self.__burn_nodes["constraint"] = self.constraint


    def __create_shader(self):

        self.shader, self.sg = libShader.get_or_create_shader("C_guide_0_shd", 'lambert')
        cmds.sets(self.shapes, edit=True, forceElement=self.sg)

        self.__burn_nodes["shader"] = self.shader
        self.__burn_nodes["sg"] = self.sg

        # rgb = libShader.get_rgb_from_position(self.position)
        rgb = (1, 1, 0)
        cmds.setAttr('%s.color' % self.shader, *rgb, type='float3')
        cmds.setAttr('%s.incandescence' % self.shader, *rgb, type='float3')
        cmds.setAttr('%s.diffuse' % self.shader, 0)

    def __post(self):
        """
        Post node creation
        """

        # Clean up trash
        try:
            cmds.delete(self.__trash)
        except Exception:
            pass

        # Burn in nodes
        cmds.setAttr("%s.snapshotNodes" % self.setup_node, json.dumps(self.__burn_nodes), type="string")
        cmds.setAttr("%s.snapshotNondag" % self.setup_node, json.dumps(self.__burn_nondag), type="string")

    def reinit(self):
        """
        """

        if not self.exists():
            raise Exception('Cannot reinit \'%s\' as guide does not exist.' % self.name)

        # Get setup node
        for key, item in self.nodes.items():
            setattr(self, key, item)

        return self

    def create(self):
        """
        """

        if self.exists():
            return self.reinit()

        self.__create_nodes()
        self.__create_attribtues()
        self.__create_aim()
        self.__create_shader()
        self.__post()

        return self

    def duplicate(self):
        """
        """

        name = libName.generate_name(*self._decompile())
        return Guide(*libName._decompile(name)[:-1]).create()

    def remove(self):
        """
        """

        parent = self.parent
        children = self.children

        if parent:
            parent.remove_child(self)

        # for key, child in self.children.items():
        for key, child in children.items():
            self.remove_child(child)

        cmds.delete(self.nondag)
        cmds.delete(self.setup_node)
        cmds.delete(self.joint)

    def compile(self):
        """
        Create a joint
        """

        orientation = cmds.getAttr("%s.rotate" % self.aim)[0]

        # joint = cmds.joint(name=libName.set_suffix(self.joint, "jnt"),
        #                    orientation=orientation,
        #                    position=self.get_translates(),
        #                    rotationOrder=self.get_axis())
        joint = cmds.joint(name=self.name.recompile(suffix="jnt"),
                           orientation=orientation,
                           position=self.get_translates(),
                           rotationOrder=self.get_axis())

        # if self.children:
        #     cmds.joint(joint, e=True, orientJoint=self.get_orient())

        cmds.select(cl=True)

        return joint
