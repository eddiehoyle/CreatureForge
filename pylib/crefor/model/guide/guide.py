#!/usr/bin/env python

'''
'''

import re
from maya import cmds
from crefor.lib import libName, libAttr, libShader
from crefor.model import Node
from crefor.model.guide.connector import Connector

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

class Guide(Node):

    SUFFIX = 'gde'
    RADIUS = 1.0
    DEFAULT_AIMS = ['world', 'local']
    UP_SCALE_VALUE = RADIUS/3.3

    def __init__(self, position, description, index=0):
        super(Guide, self).__init__(position, description, index)

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

        # self.connectors = {}
        self.trash = []

        # if cmds.objExists(self.name):
        #     self.reinit()

    def connectors2(self):
        return self.connectors

    def short_name(self):
        return None

    @property
    def parent(self):
        _parent = cmds.listRelatives(self.joint, parent=True, type='joint')
        if _parent:
            return Guide(*libName._decompile(_parent[0])[0:3]).reinit()
        return None

    @property
    def children(self):
        _children = cmds.listRelatives(self.joint, children=True, type='joint') or []
        data = {}
        for _child in _children:
            if libName.is_valid(_child):
                data[_child] = Guide(*libName._decompile(_child)[0:3]).reinit()
        return data

    @property
    def connectors(self):
        data = {}

        # Init parent connector
        if self.parent:
            data[self.parent.name] = Connector(self.parent, self).reinit()

        # Init child connectors
        for _child in self.children.values():
            data[_child.name] = Connector(self, _child).reinit()

        return data

    def long_name(self):
        return None

    def set_scale(self, value):
        '''
        Scale guide and related connectors
        '''

        if self.joint:
            libAttr.unlock_scales(self.joint)
            cmds.setAttr('%s.scale' % self.joint, value, value, value, type='float3')
            libAttr.lock_scales(self.joint, hide=True)

            for child in self.children.values():
                self.connectors[child.name].set_start_scale(value)

            if self.parent:
                self.connectors[self.parent.name].set_end_scale(value)

    def set_translates(self, vector3f):
        if self.joint:
            cmds.setAttr('%s.translate' % self.joint, *vector3f, type='float3')

    def set_debug(self, debug):
        if self.joint:
            cmds.setAttr('%s.debug' % self.joint, bool(debug))

    def has_child(self, guide):
        return guide.name in self.children

    def is_parent(self, guide):
        return guide.parent is self.parent

    def has_parent(self, guide):
        '''
        Loop up all parents
        '''

        parent = self.parent
        while parent:
            if guide.name == parent.name:
                return True
            parent = parent.parent
        return False

    def set_parent(self, guide):
        '''
        arm spine
        arm is child of spine
        '''

        if self.name == guide.name:
            return None

        if self.parent == guide:
            log.info("'%s' is already a parent of '%s'" % (guide.joint, self.joint))
            return self.parent

        if guide.has_parent(self):
            guide.remove_parent()

        if self.parent:
            self.remove_parent()

        # if self.has_child(guide):
        #     self.remove_aim(guide)

        # if guide.has_child(self):
        #     guide.remove_aim(self)

        # Store data
        guide.add_aim(self)
        log.info('\'%s\' successfully set parent: \'%s\'' % (self.joint, guide.joint))

    def add_child(self, guide):
        '''
        '''

        if self == guide:
            return None

        if guide.name in self.children:
            log.info("'%s' is already a child of '%s'" % (guide.joint, self.joint))
            return self.children[guide.name]

        if guide.parent:
            guide.remove_parent()

        if self.has_parent(guide):
            self.remove_parent()

        # Store data
        self.add_aim(guide)
        log.info('\'%s\' successfully added child: \'%s\'' % (self.joint, guide.joint))

    def add_aim(self, guide):
        '''
        self aims at guide
        self --> guide

        self is always parent
        guide is always child
        '''

        if self.name in guide.connectors:
            return guide.connectors[self.name]

        try:
            cmds.aimConstraint(guide.aim, self.aim, worldUpObject=self.up,
                               worldUpType='object',
                               offset=(0, 0, 0),
                               aimVector=(1, 0, 0),
                               upVector=(0, 1, 0),
                               mo=False)
        except Exception as e:
            print e
            print self.aim, guide.aim
            1/0

        enums = cmds.attributeQuery('aimAt', node=self.joint, listEnum=True)[0].split(':')
        enums.append(guide.aim)
        cmds.addAttr('%s.aimAt' % self.joint, e=True, en=':'.join(enums))

        con = Connector(self, guide)
        con.create()

        self.connectors[guide.name] = con
        guide.connectors[self.name] = con

        # Burn in attributes
        # cmds.setAttr('%s.parent' % guide.setup_node, self.name, type='string')
        # cmds.setAttr('%s.children' % self.setup_node, ';'.join(guide.children.keys()), type='string')

        # cmds.setAttr('%s.connectors' % self.setup_node, ';'.join(self.connectors.keys()), type='string')
        # cmds.setAttr('%s.connectors' % guide.setup_node, ';'.join(guide.connectors.keys()), type='string')

        # if self.has_parent(guide):
        # if guide.has_child(self):
            # cmds.parent(self.joint, world=True)
        cmds.parent(guide.joint, self.joint)

        aliases = cmds.aimConstraint(self.constraint, q=True, wal=True)
        for alias in aliases:
            if not cmds.listConnections('%s.%s' % (self.constraint, alias), source=True,
                                                                              destination=False,
                                                                              plugs=True):
                cmds.setAttr('%s.%s' % (self.constraint, alias), 0)

        return con

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

        self.remove_connector(guide)

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
        
        # del self.children[guide.name]
        # guide.parent = None
        cmds.parent(guide.joint, world=True)

        log.info('%s remove child: %s' % (self.name, guide.name))

    def get_parent(self):
        return self.parent

    def get_child(self, name):
        return self.children.get(name, None)

    def create_nodes(self):
        
        # Create joint and parent sphere under
        # cmds.select(cl=True)
        self.joint = cmds.createNode('joint', name=self.name)
        # cmds.select(cl=True)

        _sphere = cmds.sphere(radius=self.RADIUS, ch=False)[0]
        self.shapes = cmds.listRelatives(_sphere, type='nurbsSurface', children=True)
        cmds.parent(self.shapes, self.joint, r=True, s=True)
        cmds.setAttr('%s.drawStyle' % self.joint, 2)

        # Setup node
        self.setup_node = cmds.group(name=libName.set_suffix(self.name, 'setup'), empty=True)
        cmds.pointConstraint(self.joint, self.setup_node, mo=False)

        # for attr in ['parent', 'children', 'connectors']:
        #     cmds.addAttr(self.setup_node, ln=attr, dt='string')

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

        # Tidy up
        cmds.parent([self.up, self.aim], self.setup_node)
        self.trash.extend([_cube, _sphere])

    def create_attribtues(self):

        cmds.addAttr(self.joint, ln='debug', at='bool', min=0, max=1, dv=0)
        cmds.setAttr('%s.debug' % self.joint, k=False)
        cmds.setAttr('%s.debug' % self.joint, cb=True)
        cmds.connectAttr('%s.debug' % self.joint, '%s.displayLocalAxis' % self.aim)

    def create_aim(self):
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

    def create_shader(self):

        self.shader, self.sg = libShader.get_or_create_shader(libName.set_suffix(self.name, 'shd'), 'lambert')
        cmds.sets(self.shapes, edit=True, forceElement=self.sg)

        # rgb = libShader.get_rgb_from_position(self.position)
        rgb = (1, 1, 0)
        cmds.setAttr('%s.color' % self.shader, *rgb, type='float3')
        cmds.setAttr('%s.incandescence' % self.shader, *rgb, type='float3')
        cmds.setAttr('%s.diffuse' % self.shader, 0)

    def cleanup(self):
        '''Delete trash nodes'''

        try:
            cmds.delete(self.trash)
        except Exception:
            pass

        self.trash = []

    def reinit(self):
        '''
        '''

        if not cmds.objExists(self.name):
            log.info('Cannot reinit \'%s\' as guide does not exist.' % self.name)
            return None

        self.joint = cmds.ls(self.name)[0]
        self.shapes = cmds.listRelatives(self.joint, type='nurbsSurface', children=True)
        self.aim = cmds.ls(libName.set_suffix(self.name, 'aim'))[0]
        self.constraint = cmds.listRelatives(self.aim, children=True, type='aimConstraint')[0]

        self.sg = cmds.listConnections(self.shapes, type='shadingEngine')[0]
        self.shader = cmds.listConnections('%s.surfaceShader' % self.sg)[0]

        self.setup_node = cmds.ls(libName.set_suffix(self.name, 'setup'))[0]
        
        self.up = cmds.ls(libName.set_suffix(self.name, 'up'))[0]

        # print '-'*50
        # print 'self.joint', self.joint
        # print 'self.shapes', self.shapes
        # print 'self.aim', self.aim
        # print 'self.constraint', self.constraint
        # print 'self.sg', self.sg
        # print 'self.shader', self.shader
        # print 'self.up', self.up
        # print '-'*50

        return self

    def create(self):
        '''
        '''

        if cmds.objExists(self.name):
            return self.reinit()

        self.create_nodes()
        self.create_attribtues()
        self.create_aim()
        self.create_shader()
        self.cleanup()

        cmds.select(cl=True)

        return self.joint

