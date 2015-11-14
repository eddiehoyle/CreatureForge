#!/usr/bin/env python

"""
"""

import json
from collections import OrderedDict
from copy import deepcopy

from creatureforge.lib import libattr
from creatureforge.build._base import BuildBase
from creatureforge.control import name
from creatureforge.model.components.skeleton import ComponentSkeletonModel
from creatureforge.model.components.fk import ComponentFkModel
from creatureforge.model.components.ik import ComponentIkRpModel

from maya import cmds


class BipedBuild(BuildBase):

    SUFFIX = "rig"

    def __init__(self, *args, **kwargs):
        super(BipedBuild, self).__init__(*args, **kwargs)

        self.skeleton = None

    def _new(self):
        cmds.file(new=True, force=True)

    def _create_node(self):
        node = cmds.createNode("transform", name=self.name)
        libattr.lock_all(node)

    def _create_skeleton(self):
        skeleton_name = name.rename(self.name, secondary="skeleton")
        skeleton = ComponentSkeletonModel(*skeleton_name.tokens)
        path = "/Users/eddiehoyle/Documents/maya/projects/fishy/scenes/skeleton.mb"
        skeleton.set_path(path)
        skeleton.create()
        cmds.parent(skeleton.node, self.node)
        self.skeleton = skeleton

    def _create(self):
        self._new()
        self._create_node()
        self._create_skeleton()
        self._create_arms()
        self._create_legs()

    def _create_arms(self):
        joints = ["{0}_arm_0_shoulder_1_jnt",
                  "{0}_arm_0_elbow_0_jnt",
                  "{0}_arm_0_wrist_0_jnt"]
        for pos in ["L", "R"]:
            arm = ComponentFkModel(pos, "arm", 0, "base", 0)
            arm.set_joints(map(lambda s: s.format(pos), joints))
            arm.create()
            arm.set_shape_rotate(z=90)

            color = "blue" if pos == "R" else "red"
            for ctl in arm.get_handles().values():
                ctl.set_color(color)

    def _create_legs(self):
        joints = ["{0}_leg_0_hip_1_jnt",
                  "{0}_leg_0_knee_0_jnt",
                  "{0}_leg_0_ankle_0_jnt"]
        for pos in ["L", "R"]:
            leg = ComponentIkRpModel(pos, "leg", 0, "base", 0)
            leg.set_joints(map(lambda s: s.format(pos), joints))
            leg.set_match("translate")

            if pos == "L":
                leg.set_offset_rotate(x=180)

            leg.create()

            pv = leg.get_handle("pv")
            pv.set_shape_scale(0.5, 0.5, 0.5)
            pv.set_shape_rotate(x=-90)
            libattr.set(pv.offset, "translateZ", 5)

            color = "blue" if pos == "R" else "red"
            for ctl in leg.get_handles().values():
                ctl.set_color(color)
