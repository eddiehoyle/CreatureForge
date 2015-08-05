#!/usr/bin/env python

"""
A component has a top, setup and control node
"""

from creatureforge.model.base import Node

from maya import cmds

class Component(Node):

    SUFFIX = "cmp"

    def __init__(self, position, description, index=0):
        super(Component, self).__init__(position, description, index)

    def create(self):
        cmds.createNode("transform", name=self.node)