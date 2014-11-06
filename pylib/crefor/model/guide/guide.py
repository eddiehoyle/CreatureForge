#!/usr/bin/env python

'''
'''

from maya import cmds
from crefor.lib import libName, libAttr
from crefor.model.guide import TransformModel

class Guide(TransformModel):

    SUFFIX = 'gde'
    RADIUS = 0.5

    def __init__(self, position, description, index=0):
        super(Guide, self).__init__()

        self.position = position
        self.description = description
        self.index = index

        self.name = libName.create_name(self.position,
                                        self.description,
                                        self.index,
                                        self.SUFFIX)

        if cmds.objExists(self.name):
            raise NameError('Node already exists: %s' % self.name)

        self.transform = None
        self.shape = None
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
        
        self.transform = cmds.sphere(name=self.name, radius=self.RADIUS)[0]
        self.shape = cmds.listRelatives(self.transform, type='nurbsSurface', children=True)[0]

        libAttr.lock_rotates(self.transform)
        libAttr.lock_scales(self.transform)
        libAttr.hide_rotates(self.transform)
        libAttr.hide_scales(self.transform)
        libAttr.nonkeyable_translates(self.transform)
        libAttr.hide_vis(self.transform)

    def __create_attribtues(self):
        pass

    def init(self):
        pass

    def create(self):
        self.__create_geometry()
        self.__create_attribtues()


