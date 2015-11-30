#!/usr/bin/env python

"""
"""

import time
import logging
from collections import OrderedDict

from maya import cmds

from creatureforge.lib import libxform
from creatureforge.lib import libattr
from creatureforge.control import name
from creatureforge.control import handle
from creatureforge.model.components._base import ComponentModelBase
from creatureforge.model.gen.handle import HandleModel


logger = logging.getLogger(__name__)


class ComponentFkModel(ComponentModelBase):
    """
    Components make up parts.

    Not to be confused with controls

    Part
        Component
            Setup
            Control
                Handle
                    Shapes
    """

    def __init__(self, position, primary, primary_index, secondary,
                 secondary_index, joints=None):
        super(ComponentFkModel, self).__init__(position, primary,
                                               primary_index, secondary,
                                               secondary_index, joints=joints)
        self._register_controls()

    def _register_controls(self):
        """
        """
        print 'register fk controls', self._joints
        for index, joint in enumerate(self.get_joints()):
            ctl_name = name.rename(
                self.name,
                secondary="{0}Fk".format(self.name.secondary),
                secondary_index=index)
            ctl = HandleModel(*ctl_name.tokens)
            key = "fk{0}".format(
                index)
            self.add_control(key, ctl)

    def _create(self):
        if not self.get_joints():
            raise ValueError("Set some joints first.")
        self._create_controls()
        self._create_hiearchy()
        self._create_constraints()
        self._post_create()

    def _create_controls(self):
        for index, joint in enumerate(self.get_joints()):
            ctl_name = name.rename(
                self.name,
                secondary="fkFk".format(self.name.secondary),
                secondary_index=index)
            key = "fk{0}".format(
                index)
            ctl = self.get_control(key)
            ctl.set_style("circle")
            ctl.create()
            self.update_control(key, ctl)

            libattr.lock_translates(ctl.handle)
            libattr.lock_scales(ctl.handle)
            libxform.match(ctl.group, joint)

    def _create_hiearchy(self):
        ctls = self.get_controls().values()
        parent = ctls.pop(0)
        while ctls:
            child = ctls.pop(0)
            cmds.parent(child.group, parent.handle)
            parent = child

    def _create_constraints(self):
        for ctl, joint in zip(self.get_controls().values(), self.get_joints()):
            cmds.orientConstraint(ctl.handle, joint, mo=False)

    def _post_create(self):
        pass
