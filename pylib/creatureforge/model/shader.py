#!/usr/bin/env python

"""
"""

from maya import cmds

from creatureforge.lib import libname
from creatureforge.model.base import Node

class Shader(Node):

    SUFFIX = "shd"

    def __init__(self, position, description, index=0, shader="lambert"):
        super(Shader, self).__init__(position, description, index)

        self.__type = shader

    @property
    def type(self):
        return self.__type

    