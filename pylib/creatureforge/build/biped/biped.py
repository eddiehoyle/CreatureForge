#!/usr/bin/env python

"""
"""

import json
from collections import OrderedDict
from copy import deepcopy

from creatureforge.lib import libattr
from creatureforge.lib import libxform
from creatureforge.build._base import BuildBase
from creatureforge.control import name
from creatureforge.model.parts.root import PartRootModel
from creatureforge.model.parts.gen import PartGenModel
from creatureforge.model.components.skeleton import ComponentSkeletonModel
from creatureforge.model.components.gen import ComponentGenModel
from creatureforge.model.gen.handle import HandleModel
from creatureforge.model.parts.fk import PartFkModel
from creatureforge.model.parts.ik import PartIkRpModel
from creatureforge.build.biped.arms import AppendageArms
from creatureforge.build.biped.legs import AppendageLegs
from creatureforge.build.biped.spikes import AppendageSpikes

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

    def _create_model(self):
        model_name = name.rename(self.name, secondary="model")
        part = PartGenModel(*model_name.tokens)
        component = ComponentSkeletonModel(*model_name.tokens)

        part.add_component("model", component)
        self.add_part("model", part)

        path = "/Users/eddiehoyle/Documents/maya/projects/fishy/scenes/model.mb"
        component.set_path(path)

        component.create()
        part.create()

    def _create(self):
        self._create_skeleton()
        # self._create_model()
        # self._create_root()
        # self._create_cog()
        # self._create_shoulders()
        self._create_arms()
        self._create_legs()
        self._create_spikes()

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
        cog.set_shape_scale(8, 8, 8)
        component.add_control("cog", cog)

        joint = "C_root_0_base_0_jnt"
        libxform.match_translates(cog.group, joint)
        cmds.parentConstraint(cog.handle, joint, mo=True)

        part.create()
        self.add_part("cog", part)

    def _create_shoulders(self):
        joint = "{0}_arm_0_shoulder_0_jnt"
        for pos in ["L", "R"]:
            part = PartGenModel(pos, "arm", 0, "shoulder", 0)
            part.set_joints(map(lambda s: s.format(pos), [joint]))

            component = ComponentGenModel(pos, "arm", 0, "shoulder", 0)
            component.create()
            part.add_component("{0}_shoulder".format(pos), component)

            shoulder = HandleModel(pos, "arm", 0, "shoulder", 0)
            shoulder.create()
            shoulder.set_style("square")
            shoulder.set_shape_rotate(z=90)
            libxform.match_translates(shoulder.group, joint.format(pos))
            component.add_control("{0}_shoulder".format(pos), shoulder)

            # Set control colors
            color = "blue" if pos == "R" else "red"
            shoulder.set_color(color)
            if pos == "L":
                libattr.set(shoulder.offset, "rotateX", 180)

            cmds.parentConstraint(shoulder.handle, joint.format(pos), mo=True)

            part.create()
            self.add_part("{0}_shoulder".format(pos), part)

    def _create_arms(self):

        joints_raw = ["{0}_arm_0_shoulder_1_jnt",
                      "{0}_arm_0_elbow_0_jnt",
                      "{0}_arm_0_wrist_0_jnt"]

        for pos in ["L", "R"]:
            joints = map(lambda s: s.format(pos), joints_raw)

            arm_name = name.create(pos, "arm", 0, "base", 0, "ctl")
            arms = AppendageArms(arm_name, joints)
            arms.create()

            key = "{0}_arm".format(arm_name.position)
            arm_part = arms.get_part(key)
            self.add_part(key, arm_part)

    def _create_spikes(self):

        joint_raw = "C_spike_{0}_base_0_jnt"
        joints = [joint_raw.format(i) for i in range(14)]

        spike_name = name.create("C", "spike", 0, "base", 0, "ctl")
        spikes = AppendageSpikes(spike_name, joints)
        spikes.create()

        key = "spikes"
        spike_part = spikes.get_part(key)
        self.add_part(key, spike_part)

        # spikes_name = name.rename(self.name, secondary="spikes")
        # part = PartGenModel(*spikes_name.tokens)

        # component = ComponentGenModel(*spikes_name.tokens)
        # component.create()

        # part.add_component("spikes", component)
        # part.create()

        # joint_raw = "C_spike_{0}_base_0_jnt"
        # for index in range(14):

        #     joint = joint_raw.format(index)
        #     ctl_name = name.rename(spikes_name, secondary_index=index)
        #     ctl = HandleModel(*ctl_name.tokens)
        #     ctl.create()
        #     ctl.set_shape_rotate(z=90)
        #     ctl.set_shape_translate(x=0.5)
        #     ctl.set_shape_scale(1.3, 1.3, 1.3)

        #     component.add_control("spike_{0}".format(index), ctl)
        #     libxform.match(ctl.group, joint)
        #     cmds.parentConstraint(ctl.handle, joint, mo=True)

    def _create_legs(self):
        joints_raw = ["{0}_leg_0_hip_0_jnt",
                      "{0}_leg_0_hip_1_jnt",
                      "{0}_leg_0_knee_0_jnt",
                      "{0}_leg_0_ankle_0_jnt"]

        for pos in ["L", "R"]:
            joints = map(lambda s: s.format(pos), joints_raw)

            leg_name = name.create(pos, "leg", 0, "base", 0, "ctl")
            legs = AppendageLegs(leg_name, joints)
            legs.set_ik_joints(joints[1], joints[-1])
            legs.create()

            key = "{0}_leg".format(leg_name.position)
            leg_part = legs.get_part(key)
            self.add_part(key, leg_part)
