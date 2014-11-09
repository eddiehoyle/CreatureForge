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

class Guide(Node):

    SUFFIX = 'gde'
    RADIUS = 1.0

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

        self.__connectors = {}
        self.__children = {}
        self.__parent = None

    def short_name(self):
        return None

    def long_name(self):
        return None

    def set_translates(self, vector3f):
        if self.transform:
            cmds.setAttr('%s.translate' % self.transform, *vector3f, type='float3')

    def set_debug(self, debug):
        if self.transform:
            cmds.setAttr('%s.debug' % self.transform, bool(debug))

    def has_child(self, guide):
        return guide in self.__children.values()

    def is_parent(self, guide):
        return guide == self.__parent

    def set_parent(self, guide):
        '''
        '''

        if self.has_child(guide):
            raise RuntimeError('Guide \'%s\' is currently set as child of \'%s\', cannot set parent.' % (guide.transform,
                                                                                                         self.transform))

        if self.__parent == guide:
            print 'already has parent', guide.name
            return self.__parent

        self.__add_aim(guide)
        log.info('\'%s\' set parent: \'%s\'' % (self.transform, guide.transform))
        print 'post', self.__connectors

        # Store data
        self.__parent = guide
        guide.__children[guide.name] = guide

        return self.__connectors[self.name]

    def add_child(self, guide):
        '''
        '''

        if self.is_parent(guide):
            raise RuntimeError('Guide \'%s\' is currently set as parent of \'%s\', cannot add child.' % (guide.transform,
                                                                                                         self.transform))

        if guide.name in self.__children:
            print 'already has child', guide.name
            return self.__children[guide.name]

        guide.__add_aim(self)
        log.info('\'%s\' added child: \'%s\'' % (self.transform, guide.transform))

        # Store data
        self.__children[guide.name] = guide
        guide.__parent = guide

        return guide.__connectors[self.name]

    def remove_child(self, guide):
        print 'keys', self.__connectors.keys()
        if self.has_child(guide):

            self.__connectors[guide.name].remove()

            del self.__connectors[guide.name]
            del self.__children[guide.name]

            del guide.__connectors[self.name]
            guide.__parent = None

            log.info('Successfully removed guide: %s' % guide.name)
        return True

    def remove_parent(self):
        pass

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
            print 'found'
            return self.__connectors[guide.name]

        con = Connector(guide, self)
        con.create()

        self.__connectors[guide.name] = con
        guide.__connectors[self.name] = con

        cmds.aimConstraint(self.aim, guide.aim, worldUpObject=self.up,
                           worldUpType='object',
                           offset=(0, 0, 0),
                           aimVector=(1, 0, 0),
                           upVector=(0, 1, 0),
                           mo=False)

        enums = cmds.attributeQuery('aimAt', node=self.transform, listEnum=True)[0].split(':')
        enums.append(guide.aim)
        cmds.addAttr('%s.aimAt' % guide.transform, e=True, en=':'.join(enums))

        aliases = cmds.aimConstraint(self.constraint, q=True, wal=True)
        for index, alias in enumerate(aliases):
            if re.match('^%s' % guide.aim, alias):
                cmds.setAttr('%s.%s' % (self.constraint, alias), 1)
            else:
                cmds.setAttr('%s.%s' % (self.constraint, alias), 0)

        return con

    def set_aim(self, name):
        if self.transform:
            pass

    def __create_nodes(self):
        
        self.transform = cmds.sphere(name=self.name, radius=self.RADIUS, ch=False)[0]
        self.shapes = cmds.listRelatives(self.transform, type='nurbsSurface', children=True)

        libAttr.lock_rotates(self.transform, hide=True)
        libAttr.lock_scales(self.transform, hide=True)
        libAttr.nonkeyable_translates(self.transform)
        libAttr.hide_vis(self.transform)

        # Create up locator
        self.up = cmds.group(name=libName.set_suffix(self.name, 'up'), empty=True)
        cmds.setAttr('%s.translateY' % self.up, 1)
        # libAttr.lock_all(self.up, hide=True)

        # Create main aim transform
        self.aim = cmds.group(name=libName.set_suffix(self.name, 'aim'), empty=True)
        libAttr.lock_translates(self.aim, hide=True)
        libAttr.lock_scales(self.aim, hide=True)
        libAttr.lock_vis(self.aim, hide=True)
        libAttr.nonkeyable_rotates(self.aim, hide=True)

        libAttr.add_double(self.aim, 'jointOrientX', keyable=False)
        libAttr.add_double(self.aim, 'jointOrientY', keyable=False)
        libAttr.add_double(self.aim, 'jointOrientZ', keyable=False)

        for axis in ['X', 'Y', 'Z']:
            cmds.connectAttr('%s.rotate%s' % (self.aim, axis), '%s.jointOrient%s' % (self.aim, axis))

        # Add aim defaults
        self.world = cmds.group(name=libName.append_description(self.aim, 'world'), empty=True)
        self.custom = cmds.group(name=libName.append_description(self.aim, 'custom'), empty=True)

        libAttr.lock_all(self.world, hide=True)
        libAttr.lock_scales(self.custom, hide=True)
        libAttr.lock_vis(self.custom, hide=True)
        libAttr.nonkeyable_translates(self.custom, hide=False)
        libAttr.nonkeyable_rotates(self.custom, hide=False)

        cmds.parent([self.up, self.aim, self.world, self.custom], self.transform)

    def __create_attribtues(self):
        aliases = cmds.aimConstraint(self.constraint, q=True, tl=True)
        cmds.addAttr(self.transform, ln='aimAt', at='enum', en=':'.join(aliases))
        cmds.setAttr('%s.aimAt' % self.transform, k=False)
        cmds.setAttr('%s.aimAt' % self.transform, cb=True)

        cmds.addAttr(self.transform, ln='debug', at='bool', min=0, max=1, dv=0)
        cmds.setAttr('%s.debug' % self.transform, k=False)
        cmds.setAttr('%s.debug' % self.transform, cb=True)
        cmds.connectAttr('%s.debug' % self.transform, '%s.displayLocalAxis' % self.aim)

    def __create_aim(self):
        self.constraint = cmds.aimConstraint([self.world, self.custom],
                                             self.aim,
                                             worldUpObject=self.up,
                                             offset=(0, 0, 0),
                                             aimVector=(1, 0, 0),
                                             upVector=(0, 1, 0),
                                             worldUpType='object')[0]
        aliases = cmds.aimConstraint(self.constraint, q=True, wal=True)
        for alias in aliases:
            cmds.setAttr('%s.%s' % (self.constraint, alias), 0)
        else:
            cmds.setAttr('%s.%s' % (self.constraint, aliases[0]), 1)

    def __create_shader(self):

        self.shader, self.sg = libShader.get_or_create_shader(libName.set_suffix(self.name, 'shd'), 'lambert')
        cmds.sets(self.shapes, edit=True, forceElement=self.sg)

        rgb = libShader.get_rgb_from_position(self.position)
        cmds.setAttr('%s.color' % self.shader, *rgb, type='float3')
        cmds.setAttr('%s.incandescence' % self.shader, *rgb, type='float3')
        cmds.setAttr('%s.diffuse' % self.shader, 0)

    def reinit(self):
        '''
        '''

        self.transform = cmds.ls(self.name)[0]
        self.shapes = cmds.listRelatives(self.transform, type='nurbsSurface', children=True)

        self.sg = cmds.listConnections(self.shapes, type='shadingEngine')[0]
        self.shader = cmds.listConnections('%s.surfaceShader' % self.sg)[0]
        
        self.up = cmds.ls(libName.set_suffix(self.name, 'up'))[0]

    def create(self):
        '''
        '''

        if cmds.objExists(self.name):
            return self.reinit()

        self.__create_nodes()
        self.__create_aim()
        self.__create_attribtues()
        self.__create_shader()

        cmds.select(cl=True)

        return self.transform

