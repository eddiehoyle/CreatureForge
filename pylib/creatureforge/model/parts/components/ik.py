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
from creatureforge.model.parts.components.control import ControlHandleModel
from creatureforge.decorators import Memoized
from creatureforge.model.parts.base import ComponentModelBase


logger = logging.getLogger(__name__)


class ComponentIkScModel(ComponentModelBase):
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
        super(ComponentIkScModel, self).__init__(position, primary, primary_index, secondary, secondary_index)

        self.__joints = []
        self.__controls = []

    def get_handle(self):
        return self._dag.get("handle")

    def get_effector(self):
        return self._dag.get("effector")

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

        if not len(joints) >= 2:
            err = "Must set at least 2 joints for Ik component!"
            raise ValueError(err)

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
        self._create_ik()
        self._create_controls()
        self.__create_hiearchy()
        self.__create_constraints()

    def _create_ik(self):
        joints = self.get_joints()
        start_joint, end_joint = joints[0], joints[-1]
        handle, effector = cmds.ikHandle(sj=start_joint, ee=end_joint, sol="ikSCsolver")
        self.store("handle", handle)
        self.store("effector", effector)

    def _create_controls(self):

        # Create controls
        for index, joint in enumerate(self.get_joints()):
            ctl_name = name.rename(self.get_name(), secondary_index=index)
            ctl_tokens = name.tokenize(ctl_name)
            ctl = ControlHandleModel(*ctl_tokens)
            ctl.set_shape("circle")
            ctl.create()

            libattr.lock_rotates(ctl.get_transform())
            libattr.lock_scales(ctl.get_transform())
            libattr.lock_visibility(ctl.get_transform())

            libxform.match(ctl.get_group(), joint)

            self.__controls.append(ctl)

    def __create_hiearchy(self):
        pass

    def __create_constraints(self):
        ctls = self.get_controls()
        joints = self.get_joints()
        cmds.pointConstraint(ctls[0], joints[0])
        cmds.pointConstraint(ctls[-1], self.get_handle())


class ComponentIkRpModel(ComponentIkScModel):

    def __init__(self, position, primary, primary_index, secondary, secondary_index):
        super(ComponentIkRpModel, self).__init__(position, primary, primary_index, secondary, secondary_index)

        self.__polevector_offset = [0, 0, 0]

    def _create_ik(self):
        joints = self.get_joints()
        start_joint, end_joint = joints[0], joints[-1]
        handle, effector = cmds.ikHandle(sj=start_joint, ee=end_joint, sol="ikRPsolver")
        self.store("handle", handle)
        self.store("effector", effector)

    def _create_controls(self):
        super(ComponentIkRpModel, self)._create_controls()
        self.__add_polevector()

    def set_polevector_offset(self, x, y, z):
        self.__polevector_offset = [x, y, z]

    def get_polevector_offset(self):
        return self.__polevector_offset

    def __add_polevector(self):
        """Add pole vector for ikHandle"""
        print "PV"
        # description = description or name.get_description(name.set_description_suffix(self.ik_ctl.ctl, "pv"))
        secondary = self.get_name().secondary
        ctl_name = name.rename(
            self.get_name(),
            secondary="{secondary}Pv".format(
                secondary=secondary))
        ctl_tokens = name.tokenize(ctl_name)
        ctl = ControlHandleModel(*ctl_tokens)
        ctl.set_shape("circle")
        ctl.create()

        # Create control
        # ctl = Control(self.position, description)
        # ctl.create()
        # ctl.set_style("pyramid")

        # ctl.lock_rotates()
        # ctl.lock_scales()

        # # TODO
        # # Create aim
        # # for axis in ["X", "Y", "Z"]:
        # #     cmds.setAttr("%s.rotate%s" % (ctl.ctl, axis), k=False, cb=False)

        # # Find center of ik handle
        joints = self.get_joints()
        start_joint, end_joint = joints[0], joints[-1]
        start_pos = cmds.xform(start_joint, q=1, t=1, ws=1)
        end_pos = cmds.xform(end_joint, q=1, t=1, ws=1)

        offset = self.get_polevector_offset()
        middle_pos = libvector.average_3f(start_pos, end_pos)
        middle_pos = libvector.add_3f(middle_pos, offset)

        #  # Find center of ik handle
        # start_rot = cmds.xform(self.ik_joints[0], q=1, ro=1, ws=1)
        # end_rot = cmds.xform(self.ik_joints[-1], q=1, ro=1, ws=1)
        # middle_rot = vector.average_3f(start_rot, end_rot)

        # # Move into position
        cmds.xform(ctl.get_group(), t=middle_pos, ws=True)

        # # Create poleVector
        cmds.poleVectorConstraint(ctl.get_transform(), self.get_handle(), weight=True)

        # # Add annotation
        # mid_jnt = self.ik_joints[(len(self.ik_joints)-1)/2]
        # self.anno = anno.aim(ctl.ctl, mid_jnt, "pv")

        # self.pv_ctl = ctl
        # self.controls[ctl.name] = ctl






