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
            Control
                Shapes
        Component
            Control
    """

    def __init__(self, position, primary, primary_index, secondary,
                 secondary_index):
        super(ComponentFkModel, self).__init__(position, primary,
                                               primary_index, secondary,
                                               secondary_index)

    def __create_node(self):
        cmds.createNode("transform", name=self.name)

    def _create(self):
        if not self.joints:
            raise ValueError("Set some joints first.")
        self.__create_node()
        self.__create_controls()
        self.__create_hiearchy()
        self.__create_constraints()

    def __create_controls(self):

        # Create controls
        for index, joint in enumerate(self.joints):
            ctl_name = name.rename(self.name, secondary_index=index)
            ctl = handle.create_handle(*ctl_name.tokens)
            ctl.set_style("circle")

            libattr.lock_translates(ctl.handle)
            libattr.lock_scales(ctl.handle)

            libxform.match(ctl.group, joint)

            key = "{0}{1}".format(ctl_name.primary, index)
            self.store("controls", key, container="meta", append=True)
            self.store(key, ctl_name, container="dag")

    def __create_hiearchy(self):
        ctls = list(self.controls)
        parent = ctls.pop(0)
        while ctls:
            child = ctls.pop(0)
            cmds.parent(child.group, parent.handle)
            parent = child

    def __create_constraints(self):
        ctls = list(self.controls)
        for ctl, joint in zip(ctls, self.joints):
            cmds.orientConstraint(ctl.handle, joint, mo=False)









