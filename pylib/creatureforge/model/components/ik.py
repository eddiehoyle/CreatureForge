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


class ComponentIkModelBase(ComponentModelBase):

    def __init__(self, position, primary, primary_index, secondary,
                 secondary_index):
        super(ComponentIkModelBase, self).__init__(position, primary,
                                                   primary_index, secondary,
                                                   secondary_index)

        self._ikhandle = None
        self._effector = None

    @property
    def ikhandle(self):
        return self._ikhandle

    @property
    def effector(self):
        return self._effector

    def add_stretch(self):
        """
        """
        pass

    def _create_handles(self):
        """
        """

        joint = self.get_joints()[-1]

        ctl_name = name.rename(self.name)
        ctl = handle.create_handle(*ctl_name.tokens)
        ctl.set_style("square")
        libattr.lock_scales(ctl.handle)
        libxform.match(ctl.group, joint)

        self._handles["ik"] = ctl

    def _create_constraints(self):
        ctl = self.get_handle("ik")
        cmds.pointConstraint(ctl.handle, self.ikhandle, mo=True)
        cmds.orientConstraint(ctl.handle, self.get_joints()[-1], mo=True)

    def _create_ik(self):
        raise RuntimeError("Base class not buildable")

    def _create(self):
        if not self.get_joints():
            raise ValueError("Set some joints first.")
        self._create_ik()
        self._create_handles()
        self._create_hierarchy()
        self._create_constraints()
        self._post_create()

    def _post_create(self):
        cmds.parent(self.ikhandle, self.setup)

    def _create_hierarchy(self):
        handles = self.get_handles().values()
        groups = [ctl.group for ctl in handles]
        cmds.parent(groups, self.control)


class ComponentIkScModel(ComponentIkModelBase):
    """
    """

    SOLVER = "ikSCsolver"

    def __init__(self, *args, **kwargs):
        super(ComponentIkScModel, self).__init__(*args, **kwargs)

    def _create_ik(self):
        joints = self.get_joints()
        start_joint, end_joint = joints[0], joints[-1]
        handle, effector = cmds.ikHandle(
            sj=start_joint, ee=end_joint, sol=ComponentIkScModel.SOLVER)

        self._ikhandle = handle
        self._effector = effector


class ComponentIkRpModel(ComponentIkModelBase):

    SOLVER = "ikRPsolver"

    def __init__(self, *args, **kwargs):
        super(ComponentIkRpModel, self).__init__(*args, **kwargs)

        self._polevector_offset = [0, 0, 0]

    def _create_ik(self):
        joints = self.get_joints()
        start_joint, end_joint = joints[0], joints[-1]
        handle, effector = cmds.ikHandle(
            sj=start_joint, ee=end_joint, sol=ComponentIkRpModel.SOLVER)

        self._ikhandle = handle
        self._effector = effector

    def _create_handles(self):
        super(ComponentIkRpModel, self)._create_handles()
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
        self._handles["pv"] = ctl

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
        cmds.poleVectorConstraint(ctl.handle, self.ikhandle, weight=True)
