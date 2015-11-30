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

        self.set_joints(kwargs.get("joints", []))

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

    def _register_controls(self):
        pass

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

        # TODO
        #   ctl.group is returning None. Fix the __group caching issue
        #   in HandleModel
        for ctl in self.get_controls().values():
            if not cmds.listRelatives(ctl.group, parent=True) or []:
                print "%s <- %s" % (ctl.group, self.control)
                # cmds.parent(ctl.group, self.control)

    def create(self):
        self.__create_nodes()
        super(ComponentModelBase, self).create()
        self.__create_hierarchy()
        self.__post_create()

    def __post_create(self):
        """
        """

        print "post create on joints:", self.get_joints()
        for joint in self.get_joints():
            if not cmds.listRelatives(joint, parent=True) or []:
                cmds.parent(joint, self.setup)

    def get_controls(self):
        """Returns a list? Should it be a dictionary?

        Problems:
            How do I know the order of controls being made?
            I need to retain order for fk Chains, etc
        """
        return self._controls

    def add_control(self, key, handle):
        """Dict of handles
        """
        self._controls.update({key: handle})
        if handle.exists:
            if not cmds.listRelatives(handle.group, p=True):
                cmds.parent(handle.group, self.control)

    def update_control(self, key, control):
        """
        """
        self._controls.update({key: control})
        if control.exists:
            if not cmds.listRelatives(control.group, p=True):
                cmds.parent(control.group, self.control)

    def get_control(self, name):
        """Look up in _dag to find control string name, return an object
        """
        return self.get_controls()[name]

    def set_shape_translate(self, x=None, y=None, z=None):
        for ctl in self._controls.values():
            ctl.set_shape_translate(x, y, z)

    def set_shape_rotate(self, x=None, y=None, z=None):
        for ctl in self._controls.values():
            ctl.set_shape_rotate(x, y, z)

    def set_shape_scale(self, x=None, y=None, z=None):
        for ctl in self._controls.values():
            ctl.set_shape_scale(x, y, z)

    def get_joints(self):
        return self._joints

    def set_joints(self, joints):
        if self.exists:
            err = "Cannot set joints after part has been created!"
            raise RuntimeError(err)
        # self._joints = [j for j in joints if cmds.nodeType(j) == "joint"]
        self._joints = joints
