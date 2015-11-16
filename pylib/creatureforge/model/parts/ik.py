#!/usr/bin/env python

"""
"""

from maya import cmds

from creatureforge.control import name
from creatureforge.model.parts._base import PartModelBase
from creatureforge.model.components.ik import ComponentIkScModel
from creatureforge.model.components.ik import ComponentIkRpModel


class PartIkModelBase(PartModelBase):
    """
    TODO:
        initialise components in constructor or create?
    """

    SUFFIX = "prt"

    def __init__(self, position, primary, primary_index, secondary, secondary_index):
        super(PartIkModelBase, self).__init__(position, primary, primary_index, secondary, secondary_index)

    def _init_ik_component(self):
        raise NotImplementedError("_init_ik_component")

    def _create_ik_component(self):
        raise NotImplementedError("_create_ik_component")

    def _create(self):
        self._init_ik_component()
        self._create_ik_component()


class PartIkScModel(PartIkModelBase):
    """
    """

    def _init_ik_component(self):
        ik = ComponentIkScModel(*self.name.tokens)
        ik.set_joints(self.get_joints())
        self.add_component("ik", ik)

    def _create_ik_component(self):
        self.get_component("ik").create()


class PartIkRpModel(PartIkModelBase):

    def _init_ik_component(self):
        ik = ComponentIkRpModel(*self.name.tokens)
        ik.set_joints(self.get_joints())
        self.add_component("ik", ik)

    def _create_ik_component(self):
        self.get_component("ik").create()
