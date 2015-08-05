#!/usr/bin/env python

"""
"""

import logging

from maya import cmds

from creatureforge.lib.libname import NameHandler

# ------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------


class Node(object):
    """
    Base Maya node.
    """

    SUFFIX = "nde"

    def __init__(self, position, description, index=0):

        self.__name = NameHandler(position,
                                  description,
                                  index=index,
                                  suffix=self.SUFFIX)
        self.__node = self.__name.compile()

    @property
    def exists(self):
        return cmds.objExists(self.node)

    @property
    def node(self):
        return self.__node

    @property
    def position(self):
        return self.__name.position

    @property
    def description(self):
        return self.__name.description

    @property
    def index(self):
        return self.__name.index

    @property
    def suffix(self):
        return self.__name.suffix

    def __str__(self):
        return self.node

    def __repr__(self):
        return "<%s '%s'>" % (self.__class__.__name__, self.node)

    def __hash__(self):
        return hash(self.node)

    def __getitem__(self, index):
        return self.node[index]
