#!/usr/bin/env python

"""
"""

from copy import deepcopy

from creatureforge.lib import libattr
from creatureforge.model._base import ModuleModelStaticBase

from maya import cmds


class BuildBase(ModuleModelStaticBase):

    SUFFIX = "rig"

    def __init__(self, *args, **kwargs):
        super(BuildBase, self).__init__(*args, **kwargs)

        self._parts = {}

    def __new(self):
        cmds.file(new=True, force=True)

    def __create_node(self):
        node = cmds.createNode("transform", name=self.name)
        libattr.lock_all(node)

    def create(self):
        self.__new()
        self.__pre_create()
        super(BuildBase, self).create()
        self.__post_create()

    def __pre_create(self):
        pass

    def __post_create(self):
        for key, part in self.get_parts().iteritems():
            cmds.parent(part.node, self.node)

    def add_part(self, key, part):
        """
        """
        self._parts.update({key: part})

    def get_part(self, key):
        """
        """

        return self._parts.get(key)

    def get_parts(self):
        return deepcopy(self._parts)


class AppendageBase(object):
    pass
