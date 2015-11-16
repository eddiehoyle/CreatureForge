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
        pass

    def __create_component(self):
        component = ComponentGenModel(*self.name.tokens)
        self.add_component("root", component)

    def __create_controls(self):
        root_name = name.rename(self.name, secondary="root")
        root = HandleModel(*root_name.tokens)
        root.set_style("root")
        root.create()

        offset_name = name.rename(self.name, secondary="offset")
        offset = HandleModel(*offset_name.tokens)
        offset.set_shape_scale(0.8, 0.8, 0.8)
        offset.set_style("octagon")
        offset.create()

        cmds.parent(offset.group, root.handle)

        component = self.get_component("root")
        component.add_handle("root", root)
        component.add_handle("offset", offset)

    def _create(self):
        self.__create_component()
        self.__create_controls()

        for key, component in self.get_components().iteritems():
            component.create()
