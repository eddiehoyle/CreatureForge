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
                 secondary_index):
        super(ComponentFkModel, self).__init__(position, primary,
                                               primary_index, secondary,
                                               secondary_index)

    def _create(self):
        if not self.get_joints():
            raise ValueError("Set some joints first.")
        self.__create_controls()
        self.__create_hiearchy()
        self.__create_constraints()
        self.__post_create()

    def __create_controls(self):
        for index, joint in enumerate(self.get_joints()):
            ctl_name = name.rename(self.name, secondary_index=index)
            ctl = handle.create_handle(*ctl_name.tokens)
            ctl.set_style("circle")

            libattr.lock_translates(ctl.handle)
            libattr.lock_scales(ctl.handle)
            libxform.match(ctl.group, joint)

            key = "{0}_{1}".format(
                ctl_name.secondary, ctl_name.secondary_index)
            self.store("controls", str(ctl_name), container="meta", append=True)
            self.store(key, str(ctl_name), container="dag")

    def __create_hiearchy(self):
        ctls = self.get_controls()
        parent = ctls.pop(0)
        while ctls:
            child = ctls.pop(0)
            cmds.parent(child.group, parent.handle)
            parent = child

    def __create_constraints(self):
        for ctl, joint in zip(self.get_controls(), self.get_joints()):
            cmds.orientConstraint(ctl.handle, joint, mo=False)

    def __post_create(self):
        for ctl in self.get_controls():
            if not cmds.listRelatives(ctl.group, parent=True) or []:
                cmds.parent(ctl.group, self.control)
