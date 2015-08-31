#!/usr/bin/env python

"""
"""

import time
import logging
from collections import OrderedDict

from maya import cmds

from creatureforge.lib import libxform
from creatureforge.control import name
from creatureforge.model.parts.components.control import ControlHandleModel
from creatureforge.decorators import Memoized
from creatureforge.model.parts.base import ComponentModelBase


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

    def __init__(self, position, primary, primary_index, secondary, secondary_index):
        super(ComponentFkModel, self).__init__(position, primary, primary_index, secondary, secondary_index)

        self.__joints = []
        self.__controls = []

    def get_controls(self):
        return tuple(self.__controls)

    def get_joints(self):
        return tuple(self.__joints)

    def set_joints(self, joints):
        if self.exists():
            err = "Cannot set joints after part has been created!"
            raise RuntimeError(err)

        _joints = []
        for dag in joints:
            if cmds.nodeType(dag) == "joint":
                _joints.append(dag)

        logger.debug("Setting joints for '{name}': {joints}".format(
            name=self.get_name(), joints=_joints))
        self.__joints = _joints

    def _pre(self):
        if not self.get_joints():
            err = "Cannot create '{name}' as no joints have been set!".format(
                name=self.get_name().compile())
            raise ValueError(err)

    def _post(self):
        pass

    def _create(self):
        self.__create_controls()
        self.__create_hiearchy()
        self.__create_constraints()

    def __create_controls(self):

        # Create controls
        for index, joint in enumerate(self.get_joints()):
            ctl_name = name.rename(self.get_name(), secondary_index=index)
            ctl_tokens = name.tokenize(ctl_name)
            ctl = ControlHandleModel(*ctl_tokens)
            ctl.set_shape("circle")
            ctl.create()

            libxform.match(ctl.get_group(), joint)

            self.__controls.append(ctl)

    def __create_hiearchy(self):
        ctls = list(self.get_controls())
        parent = ctls.pop(0)
        while ctls:
            child = ctls.pop(0)
            cmds.parent(child.get_group(), parent.get_transform())
            parent = child

    def __create_constraints(self):
        for ctl, joint in zip(self.get_controls(), self.get_joints()):
            cmds.parentConstraint(ctl.get_transform(), joint, mo=False)









