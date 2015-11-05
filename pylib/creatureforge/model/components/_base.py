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

    @property
    def controls(self):
        controls = self._meta.get("controls", [])
        controls = [self._dag.get(ctl) for ctl in controls]
        models = []
        for ctl in controls:
            models.append(HandleModel(*name.initialise(ctl).tokens))
        return models

    def get_control(self, control):
        raise NotImplementedError()

    @property
    def joints(self):
        return self._dag.get("joints", [])

    def set_joints(self, joints):
        if self.exists:
            err = "Cannot set joints after part has been created!"
            raise RuntimeError(err)
        joints = [j for j in joints if cmds.nodeType(j) == "joint"]
        self.store("joints", joints, container="dag")

    # def register_control(self, ctl):
    #     ctl_name = ctl.get_name()
    #     ctl_key = (ctl_name.secondary, ctl_name.secondary_index)
    #     self._controls[ctl_key] = ctl

    # def get_control(self, secondary, secondary_index):
    #     ctl_key = (secondary, secondary_index)
    #     try:
    #         return self._controls[ctl_key]
    #     except KeyError, excp:
    #         err = "Component '{comp}' does not have control: {key}".format(
    #             comp=self.__class__.__name__, key=ctl_key)
    #         excp.args = [err]
    #         raise

    # def get_controls(self):
    #     return deepcopy(self._controls)

    # def _create(self):
    #     node = cmds.createNode("locator")
    #     node = cmds.listRelatives(node, parent=True)[0]
    #     node = cmds.rename(node, self.get_name())
    #     libattr.lock_all(node)


