#!/usr/bin/env python

'''
'''

# from maya import cmds
from crefor.model import Node
from crefor.lib import libShader

class Shader(Node):

    SUFFIX = 'shd'

    def __init__(self, position, descrption, index=0):
        super(Shader, self).__init__(position, descrption, index)

    def __create_shader(self):
        self.shader, self.sg = libShader.create_shader(self.name, 'lambert')

    def create(self):
        self.__create_shader()