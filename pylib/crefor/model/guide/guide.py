#!/usr/bin/env python

'''
'''

from maya import cmds
from collections import OrderedDict
from crefor.lib import libName, libAttr, libShader
from crefor.model import Node
from crefor.model.guide.connector import Connector

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)

class Guide(Node):

    SUFFIX = 'gde'
    RADIUS = 1.0
    DEFAULT_AIMS = ['world', 'local']
    UP_SCALE_VALUE = RADIUS/3.3

    AIM_ORDER = OrderedDict([("XY", (0, 0, 0)),
                             ("XZ", (-90, 0, 0)),
                             ("YX", (0, -180, -90)),
                             ("YZ", (0, -90, -90)),
                             ("ZX", (-90, 180, -90)),
                             ("ZY", (-90, 90, -90))])

    def __init__(self, position, description, index=0):
        super(Guide, self).__init__(position, description, index)

        self.joint = None

        # Constraint utils
        self.up = None
        self.aim = None

        # Node all setup stuff is parented under
        self.setup_node = None

        # Constraint default options
        self.world = None
        self.custom = None

        # Aim constraint
        self.constraint = None
        self.orient = None

        self.__trash = []

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
            data[_child] = Guide(*libName._decompile(_child)[0:3]).reinit()
        return data

    @property
    def connectors(self):
        '''Connectors are stored in sync with children'''
        data = {}
        for _child in self.children.values():
            data[_child.name] = Connector(self, _child).reinit()
        return data

    def exists(self):
        '''Does the guide exist in Maya?'''
        return cmds.objExists(self.name)

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

    def set_translates(self, vector3f):
        '''Set position of guide'''
        if self.joint:
            cmds.setAttr('%s.translate' % self.joint, *vector3f, type='float3')

    def set_debug(self, debug):
        '''Set debug visibility'''
        if self.joint:
            cmds.setAttr('%s.debug' % self.joint, bool(debug))

    def has_child(self, guide):
        '''Is guide an immediate child of self'''
        return guide.name in self.children

    def is_parent(self, guide):
        '''Is guide the immediate parent of self'''
        # print 'p', self.parent.joint
        # print 'g', guide.joint
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
        if guide.name in self.connectors:
            return self.connectors[guide.name]

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

        return guide

    def remove_connector(self, guide):
        '''
        Child centric connector remove
        '''
        if guide.name in self.connectors:
            self.connectors[guide.name].remove()
            del self.connectors[guide.name]

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
        self.remove_connector(guide)

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

        log.info('%s remove child: %s' % (self.name, guide.name))

    def get_parent(self):
        return self.parent

    def get_child(self, name):
        return self.children.get(name, None)

    def __create_nodes(self):
        
        # Create joint and parent sphere under
        cmds.select(cl=True)
        self.joint = cmds.createNode('joint', name=self.name)
        cmds.setAttr("%s.radius" % self.joint, cb=False)
        cmds.setAttr("%s.radius" % self.joint, l=True)
        cmds.select(cl=True)

        _sphere = cmds.sphere(radius=self.RADIUS, ch=False)[0]
        self.shapes = cmds.listRelatives(_sphere, type='nurbsSurface', children=True)
        cmds.parent(self.shapes, self.joint, r=True, s=True)
        cmds.setAttr('%s.drawStyle' % self.joint, 2)

        # Setup node
        self.setup_node = cmds.group(name=libName.set_suffix(self.name, 'setup'), empty=True)
        cmds.pointConstraint(self.joint, self.setup_node, mo=False)

        # Create up transform
        self.up = cmds.group(name=libName.set_suffix(self.name, 'up'), empty=True)
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
        self.aim = cmds.group(name=libName.set_suffix(self.name, 'aim'), empty=True)
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

    def __create_attribtues(self):

        cmds.addAttr(self.joint, ln='debug', at='bool', min=0, max=1, dv=0)
        cmds.setAttr('%s.debug' % self.joint, k=False)
        cmds.setAttr('%s.debug' % self.joint, cb=True)
        cmds.connectAttr('%s.debug' % self.joint, '%s.displayLocalAxis' % self.aim)

    def __create_aim(self):
        '''
        '''

        # Create local orient
        self.orient = cmds.orientConstraint(self.joint, self.setup_node, mo=True)[0]
        aliases = cmds.orientConstraint(self.orient, q=True, wal=True)
        targets = cmds.orientConstraint(self.orient, q=True, tl=True)
        index = targets.index(self.joint)
        condition = cmds.createNode('condition')
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
        aim_order_pma = cmds.createNode("plusMinusAverage", name="pma")
        cmds.connectAttr("%s.output3D" % aim_order_pma, "%s.offset" % self.constraint)

        for pair_index, pair in enumerate(self.AIM_ORDER.keys()):
            pair_cond = cmds.createNode("condition")
            cmds.connectAttr("%s.aimOrder" % self.joint, "%s.firstTerm" % pair_cond)
            cmds.setAttr("%s.secondTerm" % pair_cond, pair_index)

            cmds.setAttr("%s.colorIfTrue" % pair_cond, *self.AIM_ORDER[pair], type="float3")
            cmds.setAttr("%s.colorIfFalse" % pair_cond, *(0, 0, 0), type="float3")

            cmds.connectAttr("%s.outColor" % pair_cond, "%s.input3D[%s]" % (aim_order_pma, pair_index))


    def __create_shader(self):

        self.shader, self.sg = libShader.get_or_create_shader(libName.set_suffix(self.name, 'shd'), 'lambert')
        cmds.sets(self.shapes, edit=True, forceElement=self.sg)

        # rgb = libShader.get_rgb_from_position(self.position)
        rgb = (1, 1, 0)
        cmds.setAttr('%s.color' % self.shader, *rgb, type='float3')
        cmds.setAttr('%s.incandescence' % self.shader, *rgb, type='float3')
        cmds.setAttr('%s.diffuse' % self.shader, 0)

    def __cleanup(self):
        '''Delete trash nodes'''

        try:
            cmds.delete(self.__trash)
        except Exception:
            pass

        self.__trash = []

    def reinit(self):
        """
        """

        if not cmds.objExists(self.name):
            raise Exception('Cannot reinit \'%s\' as guide does not exist.' % self.name)

        self.joint = cmds.ls(self.name)[0]
        self.shapes = cmds.listRelatives(self.joint, type='nurbsSurface', children=True)
        self.aim = cmds.ls(libName.set_suffix(self.name, 'aim'))[0]
        self.constraint = cmds.listRelatives(self.aim, children=True, type='aimConstraint')[0]

        self.sg = cmds.listConnections(self.shapes, type='shadingEngine')[0]
        self.shader = cmds.listConnections('%s.surfaceShader' % self.sg)[0]

        self.setup_node = cmds.ls(libName.set_suffix(self.name, 'setup'))[0]
        
        self.up = cmds.ls(libName.set_suffix(self.name, 'up'))[0]

        return self

    def create(self):
        """
        """

        if cmds.objExists(self.name):
            return self.reinit()

        self.__create_nodes()
        self.__create_attribtues()
        self.__create_aim()
        self.__create_shader()
        self.__cleanup()

        cmds.select(cl=True)

        return self

    def remove(self):
        """
        """

        return self
