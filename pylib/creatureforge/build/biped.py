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
from creatureforge.model.components.gen import ComponentGenModel
from creatureforge.model.gen.handle import HandleModel
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
        self._create_cog()
        self._create_arms()
        self._create_legs()

    def _create_root(self):
        root_name = name.rename(self.name, secondary="root")
        root = PartRootModel(*root_name.tokens)

        # Scale controls
        component = root.get_component("root")
        component.get_control("root").set_shape_scale(6, 6, 6)
        component.get_control("offset").set_shape_scale(5, 5, 5)

        root.create()
        self.add_part("root", root)

    def _create_cog(self):
        """
        """
        cog_name = name.rename(self.name, secondary="cog")
        part = PartGenModel(*cog_name.tokens)

        component = ComponentGenModel(*cog_name.tokens)
        component.create()
        part.add_component("cog", component)

        cog = HandleModel(*cog_name.tokens)
        cog.create()
        component.add_control("cog", cog)

        part.create()
        self.add_part("cog", part)

    def _create_arms(self):
        joints_raw = ["{0}_arm_0_shoulder_1_jnt",
                      "{0}_arm_0_elbow_0_jnt",
                      "{0}_arm_0_wrist_0_jnt"]
        for pos in ["L", "R"]:
            joints = map(lambda s: s.format(pos), joints_raw)
            part = PartFkModel(pos, "arm", 0, "base", 0, joints=joints)

            # Update control colors
            fk = part.get_component("fk")
            color = "blue" if pos == "R" else "red"
            for ctl in fk.get_controls().values():
                ctl.set_color(color)
                ctl.set_shape_rotate(z=90)

            part.create()
            self.add_part("{0}_arm".format(pos), part)

    def _create_legs(self):
        joints = ["{0}_leg_0_hip_1_jnt",
                  "{0}_leg_0_knee_0_jnt",
                  "{0}_leg_0_ankle_0_jnt"]
        for pos in ["L", "R"]:
            part = PartIkRpModel(pos, "leg", 0, "base", 0)
            part.set_joints(map(lambda s: s.format(pos), joints))

            # Flip ik controls if 'L' position
            ik = part.get_component("ik")
            if pos == "L":
                ik.set_offset_rotate(x=180)
            ik.set_match("translate")

            # Update polevector controls
            # TODO:
            #   The components controls haven't been registered yet
            pv = ik.get_control("pv")
            pv.set_shape_scale(0.5, 0.5, 0.5)
            pv.set_shape_rotate(x=-90)
            libattr.set(pv.offset, "translateZ", 5)

            # Set control colors
            color = "blue" if pos == "R" else "red"
            for ctl in ik.get_controls().values():
                ctl.set_color(color)

            part.create()
            self.add_part("{0}_leg".format(pos), part)
