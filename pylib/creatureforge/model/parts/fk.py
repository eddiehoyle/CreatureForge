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

    def __init__(self, position, primary, primary_index, secondary, secondary_index):
        super(PartFkModel, self).__init__(position, primary, primary_index, secondary, secondary_index)

        self.__joints = []
        self.__fk = None

    @property
    def fk(self):
        return self.__fk

    def set_joints(self, joints):
        self.__joints = joints

    def _create_fk_component(self):
        fk = ComponentFkModel(*self.name.tokens)
        fk.set_joints(self.__joints)
        fk.create()
        self.__fk = fk

    def _create_hierarchy(self):
        cmds.parent(self.fk.node, self.node)

    def _create(self):
        self._create_fk_component()
        self._create_hierarchy()
