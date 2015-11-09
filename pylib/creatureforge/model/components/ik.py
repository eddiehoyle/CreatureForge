#!/usr/bin/env python

"""
"""

import time
import logging
from collections import OrderedDict

from maya import cmds

from creatureforge.lib import libxform
from creatureforge.lib import libattr
from creatureforge.lib import libvector
from creatureforge.control import name
from creatureforge.model.components._base import ComponentModelBase
from creatureforge.control import handle


logger = logging.getLogger(__name__)


class ComponentIkModelBase(ComponentModelBase):

    def __init__(self, position, primary, primary_index, secondary,
                 secondary_index):
        super(ComponentIkModelBase, self).__init__(position, primary,
                                                   primary_index, secondary,
                                                   secondary_index)

        self._ikhandle = None
        self._effector = None
        self._stretch = False

    @property
    def ikhandle(self):
        return self._ikhandle

    @property
    def effector(self):
        return self._effector

    def set_stretch(self, stretch):
        """
        """
        self._stretch = bool(stretch)

    def _create_controls(self):
        for index, joint in enumerate(self.get_joints()):
            ctl_name = name.rename(self.name, secondary_index=index)
            ctl = handle.create_handle(*ctl_name.tokens)
            ctl.set_style("circle")

            libattr.lock_rotates(ctl.handle)
            libattr.lock_scales(ctl.handle)
            libxform.match(ctl.group, joint)

            key = "{0}_{1}".format(
                ctl_name.secondary, ctl_name.secondary_index)
            self._controls[key] = ctl

    def _create_constraints(self):
        controls = self.get_controls().values()
        joints = self.get_joints()
        cmds.pointConstraint(controls[0], joints[0])
        cmds.pointConstraint(controls[1], self.ikhandle)

    def _create_ik(self):
        raise RuntimeError("Base class not buildable")

    def _create(self):
        if not self.get_joints():
            raise ValueError("Set some joints first.")
        self._create_ik()
        self._create_controls()
        self._create_hierarchy()
        self._create_constraints()
        self._post_create()

    def _post_create(self):
        cmds.parent(self.ikhandle, self.setup)

    def _create_hierarchy(self):
        controls = self.get_controls().values()
        groups = [ctl.group for ctl in controls]
        cmds.parent(groups, self.control)

class ComponentIkScModel(ComponentIkModelBase):
    """
    """

    def __init__(self, *args, **kwargs):
        super(ComponentIkScModel, self).__init__(*args, **kwargs)

    def _create_ik(self):
        joints = self.get_joints()
        start_joint, end_joint = joints[0], joints[-1]
        handle, effector = cmds.ikHandle(sj=start_joint, ee=end_joint, sol="ikSCsolver")

        self._ikhandle = handle
        self._effector = effector


class ComponentIkRpModel(ComponentIkModelBase):

    def __init__(self, *args, **kwargs):
        super(ComponentIkRpModel, self).__init__(*args, **kwargs)

        self._polevector_offset = [0, 0, 0]

    def _create_ik(self):
        joints = self.get_joints()
        start_joint, end_joint = joints[0], joints[-1]
        handle, effector = cmds.ikHandle(sj=start_joint, ee=end_joint, sol="ikRPsolver")

        self._ikhandle = handle
        self._effector = effector

    def _create_controls(self):
        super(ComponentIkRpModel, self)._create_controls()
        self._add_polevector_handle()

    def set_polevector_offset(self, x, y, z):
        self._polevector_offset = [x, y, z]

    def get_polevector_offset(self):
        return self._polevector_offset

    def _add_polevector_handle(self):
        """Add pole vector for ikHandle"""

        ctl_name = name.rename(
            self.name,
            secondary="{0}Pv".format(self.name.secondary))
        ctl = handle.create_handle(*ctl_name.tokens)
        ctl.set_style("pyramid")
        key = "{0}_{1}".format(
            ctl_name.secondary, ctl_name.secondary_index)
        self._controls[key] = ctl

        # Find center of ik handle
        joints = self.get_joints()
        start_joint, end_joint = joints[0], joints[-1]
        start_pos = cmds.xform(start_joint, q=1, t=1, ws=1)
        end_pos = cmds.xform(end_joint, q=1, t=1, ws=1)

        offset = self.get_polevector_offset()
        middle_pos = libvector.average_3f(start_pos, end_pos)
        middle_pos = libvector.add_3f(middle_pos, offset)
        cmds.xform(ctl.group, t=middle_pos, ws=True)

        # Add
        # cmds.poleVectorConstraint(ctl.handle, self.ikhandle, weight=True)
