#!/usr/bin/env python

'''
'''

from maya import cmds
from crefor.lib import libName, libAttr, libShader
from crefor.model.guide import GuideModel

class Guide(GuideModel):

    SUFFIX = 'gde'
    RADIUS = 0.5

    def __init__(self, position, description, index=0):
        super(Guide, self).__init__(position, description, index)

        self.up = None

    def short_name(self):
        return None

    def long_name(self):
        return None

    def get_parent(self):
        return None

    def get_child(self):
        return None

    def __create_geometry(self):
        
        self.transform = cmds.sphere(name=self.name, radius=self.RADIUS, ch=False)[0]
        self.shapes = cmds.listRelatives(self.transform, type='nurbsSurface', children=True)

        libAttr.lock_rotates(self.transform, hide=True)
        libAttr.lock_scales(self.transform, hide=True)
        libAttr.nonkeyable_translates(self.transform)
        libAttr.hide_vis(self.transform)

        # Create up locator
        self.up = cmds.group(name=libName.set_suffix(self.name, 'up'), empty=True)
        cmds.setAttr('%s.translateY' % self.up, 1)
        libAttr.lock_all(self.up, hide=True)

        cmds.parent(self.up, self.transform)

    def __create_shader(self):

        self.shader, self.sg = libShader.get_or_create_shader(libName.set_suffix(self.name, 'shd'), 'lambert')
        cmds.sets(self.shapes, edit=True, forceElement=self.sg)

        rgb = libShader.get_rgb_from_position(self.position)
        cmds.setAttr('%s.color' % self.shader, *rgb, type='float3')
        cmds.setAttr('%s.incandescence' % self.shader, *rgb, type='float3')

    def __create_attribtues(self):
        pass

    def reinit(self):

        self.transform = cmds.ls(self.name)[0]
        self.shapes = cmds.listRelatives(self.transform, type='nurbsSurface', children=True)

        self.sg = cmds.listConnections(self.shapes, type='shadingEngine')[0]
        self.shader = cmds.listConnections('%s.surfaceShader' % self.sg)[0]
        
        self.up = cmds.ls(libName.set_suffix(self.name, 'up'))[0]

    def create(self):

        if cmds.objExists(self.name):
            return self.reinit()

        self.__create_geometry()
        self.__create_attribtues()
        self.__create_shader()

        return self.transform

