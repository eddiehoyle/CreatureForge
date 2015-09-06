#!/usr/bin/env python

"""
"""

import json
from collections import OrderedDict
from copy import deepcopy

from creatureforge.lib import libattr
from creatureforge.model.base import Module
from creatureforge.model.base import ModuleModelBase

class PartModelBase(ModuleModelBase):

    SUFFIX = "prt"

    def __init__(self, *args, **kwargs):
        super(PartModelBase, self).__init__(*args, **kwargs)

        self._components = {}

    def register_component(self, key, component):
        self._components[key] = component

    def get_component(self, key):
        try:
            return self._components[key]
        except KeyError, excp:
            err = "Part '{part}' does not have component: {key}".format(
                comp=self.__class__.__name__, key=key)
            excp.args = [err]
            raise

    def get_components(self):
        return deepcopy(self._components)

    def _post(self):
        super(PartModelBase, self)._post()
        if not libattr.has(self.get_node(), "components"):
            libattr.add_string(self.get_node(), "components")

        # Reformat
        components = {}
        for key, comp in self.get_components().iteritems():
            components[key] = comp.__class__.__name__

        node = self.get_node()
        libattr.set(node, "components", json.dumps(components), type="string")
        libattr.lock(node, "components")

class ComponentModelBase(ModuleModelBase):

    suffix = "cmp"

    def __init__(self, *args, **kwargs):
        super(ComponentModelBase, self).__init__(*args, **kwargs)

        self._controls = OrderedDict()

    def __create_node(self):
        # Info meta node
        pass

    def register_control(self, ctl):
        ctl_name = ctl.get_name()
        ctl_key = (ctl_name.secondary, ctl_name.secondary_index)
        self._controls[ctl_key] = ctl

    def get_control(self, secondary, secondary_index):
        ctl_key = (secondary, secondary_index)
        try:
            return self._controls[ctl_key]
        except KeyError, excp:
            err = "Component '{comp}' does not have control: {key}".format(
                comp=self.__class__.__name__, key=ctl_key)
            excp.args = [err]
            raise

    def get_controls(self):
        return deepcopy(self._controls)
