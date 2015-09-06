#!/usr/bin/env python

"""
"""

from maya import cmds
from creatureforge.control import name
from creatureforge.model.base import ModuleModelBase
from creatureforge.model.parts.shapes import get_cvs
from creatureforge.model.parts.shapes import ControlShapesModel


class ControlHandleModel(ModuleModelBase):

    SUFFIX = "ctl"

    def __init__(self, position, primary, primary_index, secondary, secondary_index):
        super(ControlHandleModel, self).__init__(position, primary, primary_index, secondary, secondary_index)

        # TODO:
        #   Append FK to name

        self.__cvs = []

    def get_key(self):
        ctl_name = self.get_name()
        return (ctl_name.secondary, ctl_name.secondary_index)

    def __rebuild(self):
        shapes = self.get_shapes()
        if shapes:
            cmds.delete(shapes)

    def get_group(self):
        return self._dag["group"]

    def get_offset(self):
        return self._dag["offset"]

    def get_shapes(self):
        return cmds.listRelatives(self.get_node(),
                                  children=True,
                                  shapes=True,
                                  type="nurbsCurve") or []

    def get_transform(self):
        return self.get_node()

    def set_shape(self, shape):
        self.__cvs = get_cvs(shape)
        if self.exists():
            shapes = self.get_shapes()
            if shapes:
                cmds.delete(shapes)
            self.__create_shapes()

    def __create_node(self):
        cmds.select(cl=True)
        node = cmds.createNode("transform", name=self.get_name().compile())
        cmds.parent(node, self.get_offset(), r=True)

    def __create_offset(self):
        offset_name = name.rename(self.get_name(), suffix="{suffix}Offset".format(
            suffix=self.SUFFIX))
        offset = cmds.createNode("transform", name=offset_name)
        cmds.parent(offset, self.get_group(), r=True)
        self.store("offset", offset)

    def __create_group(self):
        grp_name = name.rename(self.get_name(), suffix="{suffix}Grp".format(
            suffix=self.SUFFIX))
        grp = cmds.createNode("transform", name=grp_name)
        self.store("group", grp)

    def __create_shapes(self):

        node = self.get_node()

        # Create shapes curves
        for crv in self.__cvs:
            degree = 1
            temp_curve = cmds.curve(name="temp_curve", d=degree, p=crv)
            shapes = cmds.listRelatives(temp_curve, shapes=True)
            for shape in shapes:
                cmds.parent(shape, node, shape=True, r=True)
            cmds.delete(temp_curve)

        # Rename
        shapes = cmds.listRelatives(node, shapes=True)
        for index, shape in enumerate(shapes):
            shape_name = name.rename(self.get_name().compile(), shape=True)
            cmds.rename(shape, shape_name)

    def _create(self):
        self.__create_group()
        self.__create_offset()
        self.__create_node()
        self.__create_shapes()
