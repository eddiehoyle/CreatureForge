#!/usr/bin/env python

"""
"""

import json
from collections import OrderedDict
from copy import deepcopy

from creatureforge.lib import libattr
from creatureforge.model.base import Module
from creatureforge.model.base import ModuleModelBase

from maya import cmds


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
            cmds.parent(comp.get_node(), self.get_setup())

        node = self.get_node()
        libattr.set(node, "components", json.dumps(components), type="string")
        libattr.lock(node, "components")
