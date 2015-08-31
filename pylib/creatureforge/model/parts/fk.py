#!/usr/bin/env python

"""
"""

from maya import cmds

from creatureforge.control import name
from creatureforge.model.parts.base import PartModelBase
from creatureforge.model.parts.components.fk import ComponentFkModel


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

        self.__create_fk_component()

    def get_control(self):
        return self._dag["control"]

    def get_setup(self):
        return self._dag["setup"]

    def set_joints(self, joints):
        self.__fk_component.set_joints(joints)

    def __create_node(self):
        cmds.createNode("transform", name=self.get_name())

    def __create_setup(self):
        setup_name = name.rename(self.get_name(), suffix="setup")
        setup = cmds.createNode("transform", name=setup_name)
        cmds.parent(setup, self.get_node())
        self.store("setup", setup)

    def __create_control(self):
        control_name = name.rename(self.get_name(), suffix="control")
        control = cmds.createNode("transform", name=control_name)
        cmds.parent(control, self.get_node())
        self.store("control", control)

    def _create(self):
        self.__create_node()
        self.__create_setup()
        self.__create_control()
        self.__fk_component.create()

    def __create_fk_component(self):
        raise NotImplementedError("Not finished yet!")
        self.__fk_component = ComponentFkModel(*self.tokens)
        cmds.parent(self.__fk_component.get_controls()[0].get_group(), self.control)
