
from maya import cmds

from creatureforge.control import name
from creatureforge.lib import libattr
from creatureforge.lib import libxform
from creatureforge.build._base import AppendageBase
from creatureforge.model.parts.ik import PartIkRpModel
from creatureforge.model.components.gen import ComponentGenModel
from creatureforge.model.gen.handle import HandleModel


class AppendageLegs(AppendageBase):
    """
    Arm appendage and all logic required to build 'em
    """

    def __init__(self, name, joints):
        self.name = name
        self.joints = joints
        self.ik_joints = self.joints[0], self.joints[-1]

        self._parts = {}

    def set_ik_joints(self, start, end):
        self.ik_joints = start, end

    def add_part(self, key, part):
        self._parts[key] = part

    def get_parts(self):
        return self._parts

    def get_part(self, key):
        return self._parts[key]

    def create(self):
        part = PartIkRpModel(*self.name.tokens, joints=self.ik_joints)

        # Flip ik controls if 'L' position
        ik = part.get_component("ik")
        if self.name.position == "L":
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
        color = "red" if self.name.position == "L" else "blue"
        for ctl in ik.get_controls().values():
            ctl.set_color(color)

        part.create()
        self.add_part("{0}_leg".format(self.name.position), part)

        # Create hip
        component = ComponentGenModel(self.name.position, "leg", 0, "hip", 0)
        component.create()
        part.add_component("{0}_hip".format(self.name.position), component)

        hip = HandleModel(self.name.position, "leg", 0, "hip", 0)
        hip.create()
        hip.set_style("square")
        libxform.match_translates(hip.group, self.joints[0].format(self.name.position))
        component.add_control("{0}_hip".format(self.name.position), hip)

        # Set control colors
        color = "blue" if self.name.position == "R" else "red"
        hip.set_color(color)
        if self.name.position == "L":
            libattr.set(hip.offset, "rotateX", 180)

        cmds.parentConstraint(hip.handle, self.joints[0].format(self.name.position), mo=True)
