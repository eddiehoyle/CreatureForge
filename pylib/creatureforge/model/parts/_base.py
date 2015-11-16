#!/usr/bin/env python

"""
"""

from copy import deepcopy

from maya import cmds
from creatureforge.model._base import ModuleModelStaticBase


class PartModelBase(ModuleModelStaticBase):
    """Component model base for things
    """

    SUFFIX = "prt"

    def __init__(self, *args, **kwargs):
        super(PartModelBase, self).__init__(*args, **kwargs)

        self._joints = []
        self._components = {}

    def set_joints(self, joints):
        self._joints = joints
        print "setting joints:", joints

    def get_joints(self):
        return deepcopy(self._joints)

    def get_components(self):
        """
        """

        return deepcopy(self._components)

    def add_component(self, key, component):
        """
        TODO:
            type check this is a component
            collision check on key
        """

        print "Adding component %s: %s" % (key, component)
        self._components.update({key: component})

    def get_component(self, component):
        """
        TODO:
            name check if component
            consider renaming args
        """

        return self._components.get(component)

    def __pre_create(self):
        """
        """

        pass

    def create(self):
        self.__pre_create()
        super(PartModelBase, self).create()
        self.__post_create()

    def __post_create(self):
        """
        """

        for key, component in self.get_components().iteritems():
            cmds.parent(component.node, self.node)
