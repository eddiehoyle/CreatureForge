#!/usr/bin/env python

"""
"""

from maya import cmds

from creatureforge.control import name
from creatureforge.lib import libattr
from creatureforge.lib import libconstraint
from creatureforge.model.parts._base import PartModelBase
from creatureforge.model.components.ik import ComponentIkScModel
from creatureforge.model.components.ik import ComponentIkRpModel
from creatureforge.model.components.fk import ComponentFkModel


class PartIkModelBase(PartModelBase):
    """
    TODO:
        initialise components in constructor or create?
    """

    SUFFIX = "prt"

    def __init__(self, position, primary, primary_index, secondary, secondary_index, joints=[]):
        super(PartIkModelBase, self).__init__(position, primary, primary_index, secondary, secondary_index, joints=joints)
        self._init_ik_component()

    def _init_ik_component(self):
        raise NotImplementedError("_init_ik_component")

    def _create_ik_component(self):
        ik = self.get_component("ik")
        ik.set_joints(self.get_joints())
        ik.create()

    def _create(self):
        self._create_ik_component()


class PartIkScModel(PartIkModelBase):
    """
    """

    def _init_ik_component(self):
        ik = ComponentIkScModel(*self.name.tokens)
        self.add_component("ik", ik)


class PartIkRpModel(PartIkModelBase):
    """
    """

    def _init_ik_component(self):
        ik = ComponentIkRpModel(*self.name.tokens)
        self.add_component("ik", ik)


class PartIkFkModel(PartIkModelBase):
    """
    """

    def __init__(self, position, primary, primary_index, secondary, secondary_index):
        super(PartIkFkModel, self).__init__(position, primary, primary_index, secondary, secondary_index)
        self._init_ik_component()
        self._init_fk_component()

    def _init_ik_component(self):
        ik_name = name.rename(self.name, secondary="ik")
        ik = ComponentIkRpModel(*ik_name.tokens, joints=self.get_joints())
        self.add_component("ik", ik)

    def _init_fk_component(self):
        fk_name = name.rename(self.name, secondary="fk")
        fk = ComponentFkModel(*fk_name.tokens, joints=self.get_joints())
        self.add_component("fk", fk)

    def _create_ik_component(self):
        ik = self.get_component("ik")
        ik.create()

    def _create_fk_component(self):
        fk = self.get_component("fk")
        fk.create()

    def _create_intermediate_joints(self):
        """Create intermediate joints that are driven by components
        """

        hierarchy = {}
        for joint in self.get_joints():
            hierarchy[joint] = cmds.listRelatives(joint, c=True) or []

        blendfk_joints = []
        blendik_joints = []
        blendfk_history = {}
        blendik_history = {}
        for joint in self.get_joints():
            joint_name = name.initialise(joint)
            blendfk_name = name.rename(
                joint_name,
                secondary="{0}BlendFk".format(joint_name.secondary))
            blendik_name = name.rename(
                joint_name,
                secondary="{0}BlendIk".format(joint_name.secondary))
            cmds.select(cl=True)
            blendfk_joint = cmds.duplicate(joint, name=blendfk_name, po=True)[0]
            cmds.select(cl=True)
            blendik_joint = cmds.duplicate(joint, name=blendik_name, po=True)[0]

            blendfk_history[joint] = blendfk_joint
            blendik_history[joint] = blendik_joint
            blendfk_joints.append(blendfk_joint)
            blendik_joints.append(blendik_joint)

            for blend_joint in [blendfk_joint, blendik_joint]:
                if cmds.listRelatives(blend_joint, p=True) or []:
                    cmds.parent(blend_joint, world=True)

        # Create hierarchy
        for joint in self.get_joints():
            for child_joint in hierarchy[joint]:
                cmds.parent(blendfk_history[child_joint], blendfk_history[joint])
                cmds.parent(blendik_history[child_joint], blendik_history[joint])

        # Add to components
        self.get_component("fk").set_joints(blendfk_joints)
        self.get_component("ik").set_joints(blendik_joints)

    def _create_attributes(self):
        """
        """

        libattr.add_double(self.get_component("fk").setup, "fkBlend", min=0, max=1, dv=0)
        libattr.add_double(self.get_component("ik").setup, "ikBlend", min=0, max=1, dv=1)

    def _create_connections(self):
        """
        """

        joints = self.get_joints()
        fk_joints = self.get_component("fk").get_joints()
        ik_joints = self.get_component("ik").get_joints()

        fk = self.get_component("fk")
        ik = self.get_component("ik")

        for fk_joint, ik_joint, joint in zip(fk_joints, ik_joints, joints):
            constraint = cmds.orientConstraint([fk_joint, ik_joint], joint, mo=True)[0]
            handler = libconstraint.get_handler(constraint)

            fk_attr = "{0}.fkBlend".format(fk.setup)
            ik_attr = "{0}.ikBlend".format(ik.setup)

            fk_constraint_attr = "{0}.{1}".format(
                constraint, handler.aliases[handler.targets.index(fk_joint)])
            ik_constraint_attr = "{0}.{1}".format(
                constraint, handler.aliases[handler.targets.index(ik_joint)])
            cmds.connectAttr(fk_attr, fk_constraint_attr)
            cmds.connectAttr(ik_attr, ik_constraint_attr)

        # TODO:
        #   Finish this
        # Create component connections
        rev = cmds.createNode("reverse")
        cmds.connectAttr("L_arm_0_ikfk_0_settingsShape0.ikFkBlend", "{0}.fkBlend".format(fk.setup))
        cmds.connectAttr("L_arm_0_ikfk_0_settingsShape0.ikFkBlend", rev + ".inputX")
        cmds.connectAttr(rev + ".outputX", "{0}.ikBlend".format(ik.setup))

    def _create_settings_shapes(self):
        """
        """

        loc = cmds.spaceLocator()[0]
        settings = cmds.listRelatives(loc, c=True, shapes=True)[0]
        settings = cmds.rename(settings, name.rename(self.name, suffix="settings", shape=True))

        # Parent settings shape
        for component in self.get_components().values():
            for control in component.get_controls().values():
                control.add_settings(settings)

        cmds.delete(loc)

        # Hide attrs
        for axis in ["X", "Y", "Z"]:
            for attr in ["localPosition", "localScale"]:
                libattr.set(settings, "{0}{1}".format(attr, axis), cb=False)
        libattr.add_double(settings, "ikFkBlend", min=0, max=1, dv=0)

    def _create(self):
        self._create_intermediate_joints()
        self._create_ik_component()
        self._create_fk_component()
        self._create_attributes()
        self._create_settings_shapes()
        self._create_connections()
