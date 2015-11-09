#!/usr/bin/env python

"""
"""

from copy import deepcopy
from collections import OrderedDict

from creatureforge.lib import libattr
from creatureforge.control import name
from creatureforge.model._base import ModuleModelStaticBase

from maya import cmds


class ComponentModelBase(ModuleModelStaticBase):
    """Component model base for things
    """

    SUFFIX = "cmp"

    def __init__(self, *args, **kwargs):
        super(ComponentModelBase, self).__init__(*args, **kwargs)

        self.__setup = None
        self.__control = None

        self._controls = OrderedDict()
        self._joints = []

    @property
    def control(self):
        """
        """
        return self.__control

    @property
    def setup(self):
        """
        """
        return self.__setup

    def __create_nodes(self):
        """Create component node and setup node
        """

        setup_suffix = "setup"
        setup_name = name.rename(self.name, suffix=setup_suffix)
        setup_node = cmds.createNode("transform", name=setup_name)
        libattr.lock_all(setup_node)
        self.__setup = setup_node

        control_suffix = "control"
        control_name = name.rename(self.name, suffix=control_suffix)
        control_node = cmds.createNode("transform", name=control_name)
        libattr.lock_all(control_node)
        self.__control = control_node

    def __create_hierarchy(self):
        """Parent control and setup under component
        """
        cmds.parent([self.setup, self.control], self.node)

    def create(self):
        self.__create_nodes()
        super(ComponentModelBase, self).create()
        self.__create_hierarchy()

    def get_controls(self):
        """Returns a list? Should it be a dictionary?

        Problems:
            How do I know the order of controls being made?
            I need to retain order for fk Chains, etc
        """
        return deepcopy(self._controls)

    def get_control(self, handle):
        """Look up in _dag to find control string name, return an object
        """
        controls = self.get_controls()
        return controls["handle"]

    def get_joints(self):
        return self.__joints

    def set_joints(self, joints):
        if self.exists:
            err = "Cannot set joints after part has been created!"
            raise RuntimeError(err)
        self.__joints = [j for j in joints if cmds.nodeType(j) == "joint"]
