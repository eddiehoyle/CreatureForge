#!/usr/bin/env python

"""
"""

from maya import cmds

from creatureforge.control import name
from creatureforge.model.parts._base import PartModelBase
from creatureforge.model.components.ik import ComponentIkScModel
from creatureforge.model.components.ik import ComponentIkRpModel
from creatureforge.model.components.fk import ComponentFkModel


class PartIkModelBase(PartModelBase):
    """
    TODO:
        initialise components in constructor or create?
    """

    SUFFIX = "prt"

    def __init__(self, position, primary, primary_index, secondary, secondary_index):
        super(PartIkModelBase, self).__init__(position, primary, primary_index, secondary, secondary_index)
        self._init_ik_component()

    def _init_ik_component(self):
        raise NotImplementedError("_init_ik_component")

    def _create_ik_component(self):
        ik = self.get_component("ik")
        ik.set_joints(self.get_joints())
        ik.create()

    def _create(self):
        self._create_ik_component()


class PartIkScModel(PartIkModelBase):
    """
    """

    def _init_ik_component(self):
        ik = ComponentIkScModel(*self.name.tokens)
        self.add_component("ik", ik)


class PartIkRpModel(PartIkModelBase):
    """
    """

    def _init_ik_component(self):
        ik = ComponentIkRpModel(*self.name.tokens)
        self.add_component("ik", ik)


class PartIkFkModel(PartIkModelBase):
    """
    """

    def __init__(self, position, primary, primary_index, secondary, secondary_index):
        super(PartIkFkModel, self).__init__(position, primary, primary_index, secondary, secondary_index)
        self._init_ik_component()
        self._init_fk_component()

    def _init_ik_component(self):
        ik_name = name.rename(self.name, secondary="ik")
        ik = ComponentIkRpModel(*ik_name.tokens)
        self.add_component("ik", ik)

    def _init_fk_component(self):
        fk_name = name.rename(self.name, secondary="fk")
        fk = ComponentFkModel(*fk_name.tokens)
        self.add_component("fk", fk)

    def _create_ik_component(self):
        ik = self.get_component("ik")
        ik.set_joints(self.get_joints())
        ik.create()

    def _create_fk_component(self):
        fk = self.get_component("fk")
        fk.set_joints(self.get_joints())
        fk.create()

    def _create_intermediate_joints(self):
        for joint in self.get_joints():
            pass

    def _create(self):
        self._create_intermediate_joints()
        self._create_ik_component()
        self._create_fk_component()
