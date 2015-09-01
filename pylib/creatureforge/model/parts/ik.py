#!/usr/bin/env python

"""
"""

from maya import cmds

from creatureforge.control import name
from creatureforge.model.parts.base import PartModelBase
from creatureforge.model.parts.components.ik import ComponentIkScModel
from creatureforge.model.parts.components.ik import ComponentIkRpModel


class PartIkScModel(PartModelBase):
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
        super(PartIkScModel, self).__init__(position, primary, primary_index, secondary, secondary_index)

        self._create_ik_component()

    def get_control(self):
        return self._dag["control"]

    def get_setup(self):
        return self._dag["setup"]

    def set_joints(self, joints):
        self._ik_component.set_joints(joints)

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
        self._ik_component.create()
        self.__create_hierarchy()

    def __create_hierarchy(self):
        ctl_grps = [c.get_group() for c in self._ik_component.get_controls()]
        control = self.get_control()
        cmds.parent(ctl_grps, control)
        cmds.parent(self._ik_component.get_handle(), control)

    def _create_ik_component(self):
        self._ik_component = ComponentIkScModel(*self.tokens)


class PartIkRpModel(PartIkScModel):

    def set_polevector_offset(self, x, y, z):
        self._ik_component.set_polevector_offset(x, y, z)

    def _create_ik_component(self):
        print "ikrp"
        self._ik_component = ComponentIkRpModel(*self.tokens)
