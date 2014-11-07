#!/usr/bin/env python

'''
'''

from maya import cmds
from crefor.model import DAG
from crefor.lib import libName, libShader

class Connector(DAG):

    SUFFIX = 'cnc'
    RADIUS = 1.0

    def __init__(self, parent, child):
        super(Connector, self).__init__(*libName._decompile(child.name)[:-1])

        self.parent = parent
        self.child = child

        self.start = None
        self.end = None

        self.start_cl = None
        self.end_cl = None

    def get_parent(self):
        return self.parent

    def get_child(self):
        return self.child

    def __create_geometry(self):
        self.transform = cmds.cylinder(name=self.name,
                                       p=(0, 0, 0),
                                       ax=(0, 1, 0),
                                       ssw=0,
                                       esw=360,
                                       r=self.RADIUS,
                                       hr=1,
                                       d=3,
                                       ut=0,
                                       tol=0.01,
                                       s=4,
                                       nsp=1,
                                       ch=0)[0]
        self.shapes = cmds.listRelatives(self.transform, type='nurbsSurface', children=True)

        cmds.move('%s.cv[*]' % self.transform, y=1)

        self.start, self.start_cl = cmds.cluster('%s.cv[0:1][0:3]' % self.transform)
        self.end, self.end_cl = cmds.cluster('%s.cv[2:3][0:3]' % self.transform)
        
    def __create_shader(self):

        self.shader, self.sg = libShader.get_or_create_shader(libName.set_suffix(self.name, 'shd'), 'lambert')
        cmds.sets(self.shapes, edit=True, forceElement=self.sg)

        rgb = libShader.get_rgb_from_position(self.position)
        rgb = (0.3, 0, 0)
        cmds.setAttr('%s.color' % self.shader, *rgb, type='float3')
        cmds.setAttr('%s.incandescence' % self.shader, *rgb, type='float3')

    def __create_attribtues(self):
        pass

    def init(self):
        pass

    def create(self):
        self.__create_geometry()
        self.__create_attribtues()
        self.__create_shader()
