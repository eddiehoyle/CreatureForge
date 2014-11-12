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

        self.__connectors = {}
        self.__children = {}
        self.__parent = None

        self.__trash = []

    def short_name(self):
        return None

    def long_name(self):
        return None

    @property
    def parent(self):
        ''''''
        try:
            return cmds.listRelatives(self.joint, parent=True, type='joint')[0]
        except Exception:
            return None

    @property
    def children(self):
        ''''''
        return cmds.listRelatives(self.joint, children=True, type='joint') or []

    def set_scale(self, value):
        '''
        Scale guide and related connectors
        '''

        if self.joint:
            libAttr.unlock_scales(self.joint)
            cmds.setAttr('%s.scale' % self.joint, value, value, value, type='float3')
            libAttr.lock_scales(self.joint, hide=True)

            for child in self.__children.values():
                self.__connectors[child.name].set_start_scale(value)

            if self.__parent:
                self.__connectors[self.__parent.name].set_end_scale(value)

    def set_translates(self, vector3f):
        if self.joint:
            cmds.setAttr('%s.translate' % self.joint, *vector3f, type='float3')

    def set_debug(self, debug):
        if self.joint:
            cmds.setAttr('%s.debug' % self.joint, bool(debug))

    def has_child(self, guide):
        return guide.joint in self.children

    def is_parent(self, guide):
        return guide.parent is self.parent

    def set_parent(self, guide):
        '''
        '''

        if self.has_child(guide):
            raise RuntimeError('Guide \'%s\' is currently set as child of \'%s\', cannot set parent.' % (guide.joint,
                                                                                                         self.joint))

        if self.parent == guide.joint:
            log.warning("'%s' is already '%s' parent" % (guide.joint, self.joint))
            return self.__parent

        self.__add_aim(guide)
        log.info('\'%s\' set parent: \'%s\'' % (self.joint, guide.joint))

        print 'self parent', self.parent
        print 'self children', self.children

        # Store data
        # self.__parent = guide
        # guide.__children[self.name] = self

        return self.__connectors[guide.name]

    def add_child(self, guide):
        '''
        '''

        if guide.parent:
            guide.remove_parent(guide.parent)

        if self.parent == guide.joint:
            raise RuntimeError('Guide \'%s\' is currently set as parent of \'%s\', cannot add child.' % (guide.joint,
                                                                                                         self.joint))

        # if guide.name in self.__children:
        #     log.warning("'%s' is already a child of '%s'" % (guide.joint, self.joint))
        #     return self.__children[guide.name]

        guide.__add_aim(self)
        log.info('\'%s\' added child: \'%s\'' % (self.joint, guide.joint))

        # Store data
        # self.__children[guide.name] = guide
        # guide.__parent = self

        return guide.__connectors[self.name]

    def set_aim(self, name):
        '''
        '''

        if self.joint:
            enums = cmds.attributeQuery('aimAt', node=self.joint, listEnum=True)[0].split(':')
            if name in enums:
                cmds.setAttr('%s.aimAt' % self.joint, enums.index(name))
                log.info('\'%s\' aim set to: %s' % (self.joint, name))

    def remove_child(self, guide):
        '''
        '''

        self.__remove(self, guide)

    def remove_parent(self, guide):
        '''
        '''

        self.__remove(guide, self)

    def __remove(self, parent, child):
        '''
        '''

        if parent.has_child(child) and child.is_parent(parent):

            parent.__connectors[child.name].remove()

            del parent.__connectors[child.name]
            del parent.__children[child.name]

            del child.__connectors[parent.name]
            child.__parent = None

            enums = cmds.attributeQuery('aimAt', node=parent.transform, listEnum=True)[0].split(':')
            enums.remove(child.transform)
            cmds.addAttr('%s.aimAt' % parent.transform, e=True, en=':'.join(enums))

            # Default to world
            if len(enums) == 2:
                cmds.setAttr('%s.aimAt' % parent.transform, 0)

            aliases = cmds.aimConstraint(parent.constraint, q=True, wal=True)
            for alias in aliases:
                if not cmds.listConnections('%s.%s' % (parent.constraint, alias), source=True,
                                                                                  destination=False,
                                                                                  plugs=True):
                    cmds.setAttr('%s.%s' % (parent.constraint, alias), 0)

            log.info('Successfully removed guide: %s' % child.name)

        else:
            raise RuntimeError("'%s' is not connected to '%s'" % (parent.name, child.name))

    def get_parent(self):
        return self.__parent

    def get_child(self, name):
        return self.__children.get(name, None)

    def get_children(self):
        return self.__children.values()

    def __add_aim(self, guide):
        '''
        '''

        if guide.name in self.__connectors:
            return self.__connectors[guide.name]

        con = Connector(guide, self)
        con.create()

        self.__connectors[guide.name] = con
        guide.__connectors[self.name] = con

        cmds.aimConstraint(self.aim, guide.aim, worldUpObject=guide.up,
                           worldUpType='object',
                           offset=(0, 0, 0),
                           aimVector=(1, 0, 0),
                           upVector=(0, 1, 0),
                           mo=False)

        enums = cmds.attributeQuery('aimAt', node=guide.joint, listEnum=True)[0].split(':')
        enums.append(self.joint)
        cmds.addAttr('%s.aimAt' % guide.joint, e=True, en=':'.join(enums))

        aliases = cmds.aimConstraint(guide.constraint, q=True, wal=True)
        targets = cmds.aimConstraint(guide.constraint, q=True, tl=True)
        index = targets.index(self.aim)

        condition = cmds.createNode('condition')
        cmds.setAttr('%s.secondTerm' % condition, index)
        cmds.setAttr('%s.colorIfTrueR' % condition, 1)
        cmds.setAttr('%s.colorIfFalseR' % condition, 0)
        cmds.connectAttr('%s.aimAt' % guide.joint, '%s.firstTerm' % condition)
        cmds.connectAttr('%s.outColorR' % condition, '%s.%s' % (guide.constraint, aliases[index]))
        con.nodes.append(condition)

        cmds.connectAttr('%s.outColorR' % condition, '%s.display' % con.state_node)
        cmds.setAttr('%s.aimAt' % guide.joint, index)

        cmds.parent(self.joint, guide.joint)

        return con

    def __create_nodes(self):
        
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

        # Tidy up
        cmds.parent([self.up, self.aim], self.setup_node)
        # cmds.parent(self.setup_node, self.joint)
        self.__trash.extend([_cube, _sphere])

    def __create_attribtues(self):

        cmds.addAttr(self.joint, ln='debug', at='bool', min=0, max=1, dv=0)
        cmds.setAttr('%s.debug' % self.joint, k=False)
        cmds.setAttr('%s.debug' % self.joint, cb=True)
        cmds.connectAttr('%s.debug' % self.joint, '%s.displayLocalAxis' % self.aim)

        cmds.addAttr(self.joint, ln='aimAt', at='enum', en='local')
        cmds.setAttr('%s.aimAt' % self.joint, k=False)
        cmds.setAttr('%s.aimAt' % self.joint, cb=True)

    def __create_aim(self):

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

    def reinit(self):
        '''
        '''

        self.joint = cmds.ls(self.name)[0]
        self.shapes = cmds.listRelatives(self.joint, type='nurbsSurface', children=True)

        self.sg = cmds.listConnections(self.shapes, type='shadingEngine')[0]
        self.shader = cmds.listConnections('%s.surfaceShader' % self.sg)[0]
        
        self.up = cmds.ls(libName.set_suffix(self.name, 'up'))[0]

    def create(self):
        '''
        '''

        # if cmds.objExists(self.name):
        #     return self.reinit()

        self.__create_nodes()
        self.__create_aim()
        self.__create_attribtues()
        self.__create_shader()
        self.__cleanup()

        cmds.select(cl=True)

        return self.joint

