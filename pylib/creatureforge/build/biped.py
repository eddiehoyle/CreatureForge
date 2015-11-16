#!/usr/bin/env python

"""
"""

import json
from collections import OrderedDict
from copy import deepcopy

from creatureforge.lib import libattr
from creatureforge.build._base import BuildBase
from creatureforge.control import name
from creatureforge.model.parts.root import PartRootModel
from creatureforge.model.parts.gen import PartGenModel
from creatureforge.model.components.skeleton import ComponentSkeletonModel
from creatureforge.model.parts.fk import PartFkModel
from creatureforge.model.parts.ik import PartIkRpModel

from maya import cmds


class BipedBuild(BuildBase):

    SUFFIX = "rig"

    def __init__(self, *args, **kwargs):
        super(BipedBuild, self).__init__(*args, **kwargs)

        self.skeleton = None

    def _create_skeleton(self):
        skeleton_name = name.rename(self.name, secondary="skeleton")
        part = PartGenModel(*skeleton_name.tokens)
        component = ComponentSkeletonModel(*skeleton_name.tokens)

        part.add_component("skeleton", component)
        self.add_part("skeleton", part)

        path = "/Users/eddiehoyle/Documents/maya/projects/fishy/scenes/skeleton.mb"
        component.set_path(path)

        component.create()
        part.create()

    def _create(self):
        self._create_skeleton()
        self._create_root()
        self._create_arms()
        self._create_legs()

    def _create_root(self):
        root_name = name.rename(self.name, secondary="root")
        root = PartRootModel(*root_name.tokens)
        root.create()
        self.add_part("root", root)

        for ctl in root.get_component("root").get_controls().values():
            scale = 8
            ctl.set_shape_scale(scale, scale, scale)

    def _create_arms(self):
        joints = ["{0}_arm_0_shoulder_1_jnt",
                  "{0}_arm_0_elbow_0_jnt",
                  "{0}_arm_0_wrist_0_jnt"]
        for pos in ["L", "R"]:
            part = PartFkModel(pos, "arm", 0, "base", 0)
            part.set_joints(map(lambda s: s.format(pos), joints))
            part.create()
            self.add_part("{0}_arm".format(pos), part)

            fk = part.get_component("fk")
            color = "blue" if pos == "R" else "red"
            for ctl in fk.get_controls().values():
                ctl.set_color(color)
                ctl.set_shape_rotate(z=90)

    def _create_legs(self):
        joints = ["{0}_leg_0_hip_1_jnt",
                  "{0}_leg_0_knee_0_jnt",
                  "{0}_leg_0_ankle_0_jnt"]
        for pos in ["L", "R"]:
            part = PartIkRpModel(pos, "leg", 0, "base", 0)
            part.set_joints(map(lambda s: s.format(pos), joints))

            # TODO:
            #   figure out how to set translates on a an unitialised
            #   component within a part.
            # part.get_component("ik").set_match("translate")

            part.create()
            self.add_part("{0}_leg".format(pos), part)

            ik = part.get_component("ik")
            if pos == "L":
                ik.set_offset_rotate(x=180)

            pv = ik.get_control("pv")
            pv.set_shape_scale(0.5, 0.5, 0.5)
            pv.set_shape_rotate(x=-90)
            libattr.set(pv.offset, "translateZ", 5)

            color = "blue" if pos == "R" else "red"
            for ctl in ik.get_controls().values():
                ctl.set_color(color)
                ctl.set_shape_rotate(z=90)
