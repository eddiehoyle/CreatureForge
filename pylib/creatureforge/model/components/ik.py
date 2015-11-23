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
from creatureforge.model.gen.handle import HandleModel

TRANSLATE = "translate"
ROTATE = "rotate"


class ComponentIkModelBase(ComponentModelBase):

    def __init__(self, position, primary, primary_index, secondary,
                 secondary_index):
        super(ComponentIkModelBase, self).__init__(position, primary,
                                                   primary_index, secondary,
                                                   secondary_index)

        self._ikhandle = None
        self._effector = None
        self.__match_translate = False
        self.__match_rotate = False
        self.__offset_rotate = [0, 0, 0]

        self._register_controls()

    def _register_controls(self):
        """Register ik control
        """
        ctl_name = name.rename(self.name)
        ctl = HandleModel(*ctl_name.tokens)
        self.add_control("ik", ctl)

    @property
    def ikhandle(self):
        return self._ikhandle

    @property
    def effector(self):
        return self._effector

    def set_match(self, schema):
        """Set matching logic for ik ctrl to handle
        """
        if not hasattr(schema, "__iter__"):
            schema = [schema]
        if TRANSLATE in schema:
            self.__match_translate = True

        if ROTATE in schema:
            self.__match_rotate = True

    def set_offset_rotate(self, x=None, y=None, z=None):
        """Set offsets on handle offset transform before or after creation
        """
        values = map(lambda n: float(n) if n is not None else 0, (x, y, z))
        self.__offset_rotate = values
        if self.exists:
            ctl = self.get_control("ik")
            libattr.set(ctl.offset, "rotate", *self.__offset_rotate, type="float3")

    def add_stretch(self):
        """
        """
        pass

    def _create_controls(self):
        """
        """

        joint = self.get_joints()[-1]

        ctl = self.get_control("ik")
        ctl.set_style("square")
        ctl.create()
        libattr.set(ctl.offset, "rotate", *self.__offset_rotate, type="float3")

        libattr.lock_scales(ctl.handle)

        if self.__match_translate:
            libxform.match_translates(ctl.group, joint)
        if self.__match_rotate:
            libxform.match_rotates(ctl.group, joint)

        self.add_control("ik", ctl)

    def _create_constraints(self):
        ctl = self.get_control("ik")
        cmds.pointConstraint(ctl.handle, self.ikhandle, mo=True)
        cmds.orientConstraint(ctl.handle, self.get_joints()[-1], mo=True)

    def _create_ik(self):
        raise RuntimeError("Base class not buildable")

    def __pre_create(self):
        """Special checks to block creation of component if any special
        haven't been applied yet.
        """

        if not self.get_joints():
            raise ValueError("No joints set.")

        if not any([self.__match_rotate, self.__match_translate]):
            raise ValueError("No matching schema set for {0}".format(
                self.__class__.__name__))

    def _create(self):
        self.__pre_create()
        self._create_ik()
        self._create_controls()
        self._create_constraints()
        self._post_create()

    def _post_create(self):
        cmds.parent(self.ikhandle, self.setup)


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

    def _register_controls(self):
        super(ComponentIkRpModel, self)._register_controls()
        pv_name = name.rename(
            self.name,
            secondary="{0}Pv".format(self.name.secondary))
        pv = HandleModel(*pv_name.tokens)
        self.add_control("pv", pv)

    def _create_ik(self):
        joints = self.get_joints()
        start_joint, end_joint = joints[0], joints[-1]
        handle, effector = cmds.ikHandle(
            sj=start_joint, ee=end_joint, sol=ComponentIkRpModel.SOLVER)

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

        ctl = self.get_control("pv")
        ctl.set_style("pyramid")
        ctl.create()
        self.add_control("pv", ctl)

        # Find center of ik handle
        joints = self.get_joints()
        start_joint, end_joint = joints[0], joints[-1]
        start_pos = cmds.xform(start_joint, q=1, t=1, ws=1)
        end_pos = cmds.xform(end_joint, q=1, t=1, ws=1)

        offset = self.get_polevector_offset()
        middle_pos = libvector.average_3f(start_pos, end_pos)
        middle_pos = libvector.add_3f(middle_pos, offset)
        cmds.xform(ctl.group, t=middle_pos, ws=True)

        cmds.poleVectorConstraint(ctl.handle, self.ikhandle, weight=True)
