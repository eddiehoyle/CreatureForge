#!/usr/bin/env python

"""
A component has a top, setup and control node
"""

from creatureforge.lib import libname
# from creatureforge.decorators import exists
from creatureforge.model.base import Node

from maya import cmds


def variable_tester(target):
    def deco(function):
        def inner(self, *args, **kwargs):
            if getattr(self, target) is not None:
                return function(self, *args, **kwargs)
        return inner
    return deco


class Component(Node):

    @staticmethod
    def validate(node):
        if not cmds.objExists(node):
            raise Exception("Node doesn't exist: {node}".format(node=node))
        return node

    SUFFIX = "cmp"

    def __init__(self, position, description, index=0):
        super(Component, self).__init__(position, description, index)

        self.__top = None
        self.__setup = None
        self.__control = None

    @property
    def top(self):
        return self.__top

    @property
    def setup(self):
        return self.__setup

    @property
    def control(self):
        return self.__control

    def __create_top(self):
        self.__top = cmds.createNode("transform", name=self.node)

    def __create_setup(self):
        name = libname.rename(self.node, suffix="setup")
        self.__setup = cmds.createNode("transform", name=name)

    def __create_control(self):
        name = libname.rename(self.node, suffix="control")
        self.__control = cmds.createNode("transform", name=name)

    def __create_hierarchy(self):
        cmds.parent([self.setup, self.control], self.top)

    def create(self):
        self.__create_top()
        self.__create_setup()
        self.__create_control()
        self.__create_hierarchy()
