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

        self.set_joints(kwargs.get("joints", []))

    def set_joints(self, joints):
        self._joints = joints
        for component in self.get_components().values():
            component.set_joints(joints)
            component._register_controls()

    def get_joints(self):
        return self._joints

    def get_components(self):
        """
        """

        return self._components

    def add_component(self, key, component):
        """
        TODO:
            type check this is a component
            collision check on key
        """

        print "Adding component %s: %s" % (key, component)
        self._components.update({key: component})
        if self.exists:
            cmds.parent(component.node, self.node)

    def get_component(self, key):
        """Get specific component
        """
        try:
            return self._components[key]
        except KeyError as e:
            err = "Part '{0}' does not have '{1}' component.".format(
                self.name, key)
            e.args = [err]
            raise

    def __pre_create(self):
        """
        """

        if not self.get_components():
            raise ValueError("No components added to part yet.")

    def create(self):
        self.__pre_create()
        super(PartModelBase, self).create()
        self.__post_create()

    def __post_create(self):
        """
        """

        for key, component in self.get_components().iteritems():
            cmds.parent(component.node, self.node)
