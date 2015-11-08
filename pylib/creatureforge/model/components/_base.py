#!/usr/bin/env python

"""
"""

from creatureforge.control import name

from creatureforge.model.gen.handle import HandleModel
from creatureforge.model._base import ModuleModelBase

from maya import cmds


class ComponentModelBase(ModuleModelBase):
    """Component model base for things
    """

    SUFFIX = "cmp"

    def __init__(self, *args, **kwargs):
        super(ComponentModelBase, self).__init__(*args, **kwargs)

        self.__setup = None
        self.__control = None

    @property
    def control(self):
        """
        """
        return self.dag.get("control")

    @property
    def setup(self):
        """
        """
        return self.dag.get("setup")

    def __create_nodes(self):
        """Create component node and setup node
        """

        # Create setup node
        setup_suffix = "setup"
        setup_name = name.rename(self.name, suffix=setup_suffix)
        cmds.createNode("transform", name=setup_name)
        self.store("setup", str(setup_name), container="dag")

        control_suffix = "control"
        control_name = name.rename(self.name, suffix=control_suffix)
        cmds.createNode("transform", name=control_name)
        self.store("control", str(control_name), container="dag")

    def __setup_hierarchy(self):
        """Parent control and setup under component
        """

        cmds.parent([self.control, self.setup], self.node)

    def create(self):
        self.__create_nodes()
        super(ComponentModelBase, self).create()
        self.__setup_hierarchy()

    def get_controls(self):
        """Returns a list? Should it be a dictionary?

        Problems:
            How do I know the order of controls being made?
            I need to retain order for fk Chains, etc
        """
        controls = self._meta.get("controls", [])
        models = []
        for ctl in controls:
            models.append(self.get_control(ctl))
        return models

    def get_control(self, handle):
        """Look up in _dag to find control string name, return an object
        """

        ctl_name = name.initialise(handle)
        ctl_key = "{0}_{1}".format(ctl_name.secondary, ctl_name.secondary_index)
        ctl = self._dag.get(ctl_key)
        try:
            model = HandleModel(*ctl_name.tokens)

        # TODO:
        #   Better exception handling
        except Exception:
            print "Component '{0}' does not have handle: {1}'".format(
                self, ctl)

        return model

    def get_joints(self):
        return self._dag.get("joints", [])

    def set_joints(self, joints):
        if self.exists:
            err = "Cannot set joints after part has been created!"
            raise RuntimeError(err)
        joints = [j for j in joints if cmds.nodeType(j) == "joint"]
        self.store("joints", joints, container="dag")
