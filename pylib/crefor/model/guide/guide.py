#!/usr/bin/env python

'''
'''

from maya import cmds
from crefor.lib import libName, libAttr, libShader
from crefor.model import Node
from crefor.model.guide.connector import Connector

class Guide(Node):

    SUFFIX = 'gde'
    RADIUS = 1
    DEBUG = True

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

    def short_name(self):
        return None

    def long_name(self):
        return None

    def set_translates(self, vector3f):
        if self.transform:
            cmds.setAttr('%s.translate' % self.transform, *vector3f, type='float3')


    def set_parent(self, parent):
        con = Connector(parent, self)
        con.create()
        return con

    def get_parent(self):
        return None

    def get_child(self):
        return None

    def __create_nodes(self):
        
        self.transform = cmds.sphere(name=self.name, radius=self.RADIUS, ch=False)[0]
        self.shapes = cmds.listRelatives(self.transform, type='nurbsSurface', children=True)

        libAttr.lock_rotates(self.transform, hide=True)
        libAttr.lock_scales(self.transform, hide=True)
        libAttr.nonkeyable_translates(self.transform)
        libAttr.hide_vis(self.transform)

        cmds.addAttr(self.transform, ln='debug', at='bool', min=0, max=1, dv=0)
        cmds.setAttr('%s.debug' % self.transform, k=False)
        cmds.setAttr('%s.debug' % self.transform, cb=True)

        # Create up locator
        self.up = cmds.group(name=libName.set_suffix(self.name, 'up'), empty=True)
        cmds.setAttr('%s.translateY' % self.up, 1)
        libAttr.lock_all(self.up, hide=True)

        # Create main aim transform
        self.aim = cmds.group(name=libName.set_suffix(self.name, 'aim'), empty=True)
        libAttr.lock_translates(self.aim, hide=True)
        libAttr.lock_scales(self.aim, hide=True)
        libAttr.lock_vis(self.aim, hide=True)
        libAttr.nonkeyable_rotates(self.aim, hide=True)

        libAttr.add_double(self.aim, 'jointOrientX', keyable=False)
        libAttr.add_double(self.aim, 'jointOrientY', keyable=False)
        libAttr.add_double(self.aim, 'jointOrientZ', keyable=False)
        cmds.connectAttr('%s.debug' % self.transform, '%s.displayLocalAxis' % self.aim)

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
        pass

    def __create_aim(self):

        con = cmds.aimConstraint([self.world, self.custom], self.aim, worldUpObject=self.up, offset=(0, 0, 0),
                                 aimVector=(1, 0, 0), upVector=(0, 1, 0), worldUpType='object')[0]
        aliases = cmds.aimConstraint(con, q=True, wal=True)
        for alias in aliases:
            cmds.setAttr('%s.%s' % (con, alias), 0)
        else:
            cmds.setAttr('%s.%s' % (con, aliases[0]), 1)

    def __create_shader(self):

        self.shader, self.sg = libShader.get_or_create_shader(libName.set_suffix(self.name, 'shd'), 'lambert')
        cmds.sets(self.shapes, edit=True, forceElement=self.sg)

        rgb = libShader.get_rgb_from_position(self.position)
        cmds.setAttr('%s.color' % self.shader, *rgb, type='float3')
        cmds.setAttr('%s.incandescence' % self.shader, *rgb, type='float3')

    def reinit(self):

        self.transform = cmds.ls(self.name)[0]
        self.shapes = cmds.listRelatives(self.transform, type='nurbsSurface', children=True)

        self.sg = cmds.listConnections(self.shapes, type='shadingEngine')[0]
        self.shader = cmds.listConnections('%s.surfaceShader' % self.sg)[0]
        
        self.up = cmds.ls(libName.set_suffix(self.name, 'up'))[0]

    def create(self):

        if cmds.objExists(self.name):
            return self.reinit()

        self.__create_nodes()
        self.__create_aim()
        self.__create_attribtues()
        self.__create_shader()

        if self.DEBUG:
            cmds.setAttr('%s.debug' % self.transform, True)

        return self.transform

