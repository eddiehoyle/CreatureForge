#!/usr/bin/env python

"""
"""

from maya import cmds

from creatureforge.control import name
from creatureforge.model.parts._base import PartModelBase
from creatureforge.model.components.gen import ComponentGenModel
from creatureforge.model.gen.handle import HandleModel
from creatureforge.control import name


class PartRootModel(PartModelBase):
    """
    Generic empty part with no components
    """

    SUFFIX = "prt"

    def __init__(self, position, primary, primary_index, secondary, secondary_index):
        super(PartRootModel, self).__init__(position, primary, primary_index, secondary, secondary_index)
        self._init_root_component()

    def _init_root_component(self):
        component = ComponentGenModel(*self.name.tokens)
        self.add_component("root", component)

        # Create controls
        root_name = name.rename(self.name, secondary="root")
        root = HandleModel(*root_name.tokens)
        component.add_control("root", root)

        offset_name = name.rename(self.name, secondary="offset")
        offset = HandleModel(*offset_name.tokens)
        component.add_control("offset", offset)

    def _create_component(self):
        root = self.get_component("root")
        root.create()

    def _create_controls(self):
        component = self.get_component("root")

        root = component.get_control("root")
        root.set_style("root")
        root.create()

        offset = component.get_control("offset")
        offset.set_style("octagon")
        offset.create()

        cmds.parent(offset.group, root.handle)

    def _create(self):
        self._create_component()
        self._create_controls()
