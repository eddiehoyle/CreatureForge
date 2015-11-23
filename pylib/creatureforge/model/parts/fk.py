#!/usr/bin/env python

"""
"""

from maya import cmds

from creatureforge.control import name
from creatureforge.model.parts._base import PartModelBase
from creatureforge.model.components.fk import ComponentFkModel


class PartFkModel(PartModelBase):
    """
    Components make up parts.

    Not to be confused with controls

    Part
        Component
            Control
                Shapes
        Component
            Control
    """

    SUFFIX = "prt"

    def __init__(self, position, primary, primary_index, secondary, secondary_index, joints=None):
        super(PartFkModel, self).__init__(position, primary, primary_index, secondary, secondary_index, joints=joints)
        self._init_fk_component()

    def _init_fk_component(self):
        fk = ComponentFkModel(*self.name.tokens, joints=self.get_joints())
        self.add_component("fk", fk)

    def _create_fk_component(self):
        fk = self.get_component("fk")
        fk.set_joints(self.get_joints())
        fk.create()

    def _create(self):
        self._create_fk_component()
