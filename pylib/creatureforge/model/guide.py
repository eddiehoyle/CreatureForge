#!/usr/bin/env python

"""
"""

from creatureforge.model.base import Node


class Guide(Node):

    SUFFIX = "gde"

    def __init__(self, position, description, index=0):
        super(Guide, self).__init__(position, description, index)


class Up(Node):

    SUFFIX = "gde"

    def __init__(self, guide):
        pass


class Connector(Node):

    SUFFIX = "cnc"

    def __init__(self, child, parent):
        pass
