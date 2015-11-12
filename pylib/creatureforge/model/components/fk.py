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
        self._create_handles()
        self._create_hiearchy()
        self._create_constraints()
        self._post_create()

    def _create_handles(self):
        for index, joint in enumerate(self.get_joints()):
            ctl_name = name.rename(self.name, secondary_index=index)
            ctl = handle.create_handle(*ctl_name.tokens)
            ctl.set_style("circle")

            libattr.lock_translates(ctl.handle)
            libattr.lock_scales(ctl.handle)
            libxform.match(ctl.group, joint)

            key = "{0}{1}".format(ctl_name.secondary, ctl_name.secondary_index)
            self._handles[key] = ctl

    def _create_hiearchy(self):
        ctls = self.get_handles().values()
        parent = ctls.pop(0)
        while ctls:
            child = ctls.pop(0)
            cmds.parent(child.group, parent.handle)
            parent = child

    def _create_constraints(self):
        for ctl, joint in zip(self.get_handles().values(), self.get_joints()):
            cmds.orientConstraint(ctl.handle, joint, mo=False)

    def _post_create(self):
        for ctl in self.get_handles().values():
            if not cmds.listRelatives(ctl.group, parent=True) or []:
                cmds.parent(ctl.group, self.control)
