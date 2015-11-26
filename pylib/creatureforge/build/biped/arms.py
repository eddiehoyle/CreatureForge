
from creatureforge.control import name
from creatureforge.build._base import AppendageBase
from creatureforge.model.parts.fk import PartFkModel


class AppendageArms(AppendageBase):
    """
    Arm appendage and all logic required to build 'em
    """

    def __init__(self, name, joints):
        self.name = name
        self.joints = joints

        self._parts = {}

    def add_part(self, key, part):
        self._parts[key] = part

    def get_parts(self):
        return self._parts

    def get_part(self, key):
        return self._parts[key]

    def create(self):
        print "creating appendage"
        name.initialise(self.joints[0])
        part = PartFkModel(*self.name.tokens, joints=self.joints)

        # Update control colors
        fk = part.get_component("fk")
        color = "blue" if self.name.position == "R" else "red"
        for ctl in fk.get_controls().values():
            ctl.set_color(color)
            ctl.set_shape_rotate(z=90)

        part.create()
        self.add_part("{0}_arm".format(self.name.position), part)
