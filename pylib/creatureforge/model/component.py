#!/usr/bin/env python

"""
A component has a top, setup and control node
"""

from creatureforge.lib import libname
from creatureforge.model.base import Node

from maya import cmds


class Component(Node):

    # @staticmethod
    # def validate(node):
    #     if not cmds.objExists(node):
    #         raise Exception("Node doesn't exist: {node}".format(node=node))
    #     return node

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

    def __create_nodes(self):
        self.__top = cmds.createNode("transform", name=self.node)

        name = libname.rename(self.node, suffix="setup")
        self.__setup = cmds.createNode("transform", name=name)

        name = libname.rename(self.node, suffix="control")
        self.__control = cmds.createNode("transform", name=name)

    def __create_hierarchy(self):
        cmds.parent([self.setup, self.control], self.top)

    def create(self):
        self.__create_nodes()
        self.__create_hierarchy()
