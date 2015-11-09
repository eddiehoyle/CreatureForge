#!/usr/bin/env python

"""
Control handle model
"""

import sys

from maya import cmds

from creatureforge.lib import libattr
from creatureforge.lib import libmaya
from creatureforge.control import name
from creatureforge.model._base import ModuleModelDynamicBase


class Shapes(object):
    """Shapes CV constants
    """

    # SPHERE = [((6.123233995736766e-17, 1.0, 0.0), (-0.25881904510252068, 0.96592582628906831, 0.0), (-0.49999999999999989, 0.86602540378443871, 0.0), (-0.70710678118654746, 0.70710678118654757, 0.0), (-0.8660254037844386, 0.50000000000000011, 0.0), (-0.9659258262890682, 0.25881904510252096, 0.0), (-1.0, 2.8327694488239898e-16, 0.0), (-0.96592582628906842, -0.25881904510252046, 0.0), (-0.86602540378443893, -0.49999999999999972, 0.0), (-0.70710678118654791, -0.70710678118654735, 0.0), (-0.50000000000000044, -0.8660254037844386, 0.0), (-0.25881904510252129, -0.96592582628906831, 0.0), (-5.330771254230592e-16, -1.0000000000000002, 0.0), (0.2588190451025203, -0.96592582628906865, 0.0), (0.49999999999999961, -0.86602540378443915, 0.0), (0.70710678118654735, -0.70710678118654813, 0.0), (0.8660254037844386, -0.50000000000000067, 0.0), (0.96592582628906842, -0.25881904510252152, 0.0), (1.0000000000000004, -7.273661547324616e-16, 0.0), (0.96592582628906898, 0.25881904510252013, 0.0), (0.86602540378443948, 0.49999999999999956, 0.0), (0.70710678118654846, 0.70710678118654735, 0.0), (0.500000000000001, 0.86602540378443871, 0.0), (0.25881904510252179, 0.96592582628906853, 0.0), (9.49410759657493e-16, 1.0000000000000004, 0.0)),
    # CROSS = [[[-0.33310534961812344, 0.0, 0.33310534961812344], [-0.99931604885437031, 0.0, 0.33310534961812344], [-0.99931604885437031, 0.0, -0.33310534961812344], [-0.33310534961812344, 0.0, -0.33310534961812344], [-0.33310534961812344, 0.0, -0.99931604885437031], [0.33310534961812344, 0.0, -0.99931604885437031], [0.33310534961812344, 0.0, -0.33310534961812344], [0.99931604885437031, 0.0, -0.33310534961812344], [0.99931604885437031, 0.0, 0.33310534961812344], [0.33310534961812344, 0.0, 0.33310534961812344], [0.33310534961812344, 0.0, 0.99931604885437031], [-0.33310534961812344, 0.0, 0.99931604885437031], [-0.33310534961812344, 0.0, 0.33310534961812344]]]
    # ARROW_SINGLE = [[[-1.0, 0.0, 1.0], [-1.0, 0.0, -1.0], [-2.0, 0.0, -1.0], [0.0, 0.0, -3.0], [2.0, 0.0, -1.0], [1.0, 0.0, -1.0], [1.0, 0.0, 1.0], [-1.0, 0.0, 1.0]]]
    # ARROW_DOUBLE = [[[-1.0, 0.0, 2.0], [-1.0, 0.0, -1.0], [-2.0, 0.0, -1.0], [0.0, 0.0, -3.0], [2.0, 0.0, -1.0], [1.0, 0.0, -1.0], [1.0, 0.0, 2.0], [2.0, 0.0, 2.0], [0.0, 0.0, 4.0], [-2.0, 0.0, 2.0], [-1.0, 0.0, 2.0]]]
    # ARROW_TRIPLE = [[[-1.0, 0.0, 1.0], [-1.0, 0.0, 3.0], [-2.0, 0.0, 3.0], [0.0, 0.0, 5.0], [2.0, 0.0, 3.0], [1.0, 0.0, 3.0], [1.0, 0.0, -3.0], [2.0, 0.0, -3.0], [0.0, 0.0, -5.0], [-2.0, 0.0, -3.0], [-1.0, 0.0, -3.0], [-1.0, 0.0, -1.0], [-3.0, 0.0, -1.0], [-3.0, 0.0, -2.0], [-5.0, 0.0, 0.0], [-3.0, 0.0, 2.0], [-3.0, 0.0, 1.0], [-1.0, 0.0, 1.0]]]
    # ARROW_QUAD = [[[-1.0, 0.0, -1.0], [-1.0, 0.0, -3.0], [-2.0, 0.0, -3.0], [0.0, 0.0, -5.0], [2.0, 0.0, -3.0], [1.0, 0.0, -3.0], [1.0, 0.0, -1.0], [3.0, 0.0, -1.0], [3.0, 0.0, -2.0], [5.0, 0.0, 0.0], [3.0, 0.0, 2.0], [3.0, 0.0, 1.0], [1.0, 0.0, 1.0], [1.0, 0.0, 3.0], [2.0, 0.0, 3.0], [0.0, 0.0, 5.0], [-2.0, 0.0, 3.0], [-1.0, 0.0, 3.0], [-1.0, 0.0, 1.0], [-3.0, 0.0, 1.0], [-3.0, 0.0, 2.0], [-5.0, 0.0, 0.0], [-3.0, 0.0, -2.0], [-3.0, 0.0, -1.0], [-1.0, 0.0, -1.0]]]

    SQUARE = [((-1, 0, 1,), (-1, 0, -1), (1, 0, -1), (1, 0, 1), (-1, 0, 1))]
    CIRCLE = [[[0.0, 0.0, 1.0], [-0.26, 0.0, 0.97], [-0.5, 0.0, 0.87],
               [-0.71, 0.0, 0.71], [-0.87, 0.0, 0.5], [-0.97, 0.0, 0.26],
               [-1.0, 0.0, 0.0], [-0.97, -0.0, -0.26], [-0.87, -0.0, -0.5],
               [-0.71, -0.0, -0.71], [-0.5, -0.0, -0.87], [-0.26, -0.0, -0.97],
               [-0.0, -0.0, -1.0], [0.26, -0.0, -0.97], [0.5, -0.0, -0.87],
               [0.71, -0.0, -0.71], [0.87, -0.0, -0.5], [0.97, -0.0, -0.26],
               [1.0, -0.0, -0.0], [0.97, 0.0, 0.26], [0.87, 0.0, 0.5],
               [0.71, 0.0, 0.71], [0.5, 0.0, 0.87], [0.26, 0.0, 0.97],
               [0.0, 0.0, 1.0]]]
    PYRAMID = [[[0.0, 0.54, 0.0], [-1.0, -1.0, 1.0], [-1.0, -1.0, -1.0],
                [0.0, 0.54, 0.0], [-1.0, -1.0, -1.0], [1.0, -1.0, -1.0],
                [0.0, 0.54, 0.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0],
                [0.0, 0.54, 0.0], [1.0, -1.0, 1.0], [-1.0, -1.0, 1.0]]]
    SEMI_CIRCLE = [[[0.0, 0.0, 1.0], [-0.26, 0.0, 0.97], [-0.5, 0.0, 0.87],
                    [-0.71, 0.0, 0.71], [-0.87, 0.0, 0.5], [-0.97, 0.0, 0.26],
                    [-1.0, 0.0, 0.0], [-0.97, -0.0, -0.26],
                    [-0.87, -0.0, -0.5], [-0.71, -0.0, -0.71],
                    [-0.5, -0.0, -0.87], [-0.26, -0.0, -0.97],
                    [-0.0, -0.0, -1.0]]]
    CUBE = [[[-1.0, 1.0, -1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0],
             [-1.0, 1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, -1.0, -1.0],
             [1.0, -1.0, -1.0], [1.0, 1.0, -1.0], [1.0, -1.0, -1.0],
             [1.0, -1.0, 1.0], [1.0, 1.0, 1.0], [1.0, -1.0, 1.0],
             [-1.0, -1.0, 1.0], [-1.0, 1.0, 1.0], [-1.0, -1.0, 1.0],
             [-1.0, -1.0, -1.0]]]


class Colors:

    YELLOW = 17
    RED = 13


def get_cvs(style):
    # TODO:
    #   Validate shape name against Shapes map
    return getattr(Shapes, str(style.upper()))


def get_color(color):
    # TODO:
    #   Validate color names
    return getattr(Colors, str(color.upper()))


def exists(func):
    def wraps(*args, **kwargs):
        node = args[0].node
        if not cmds.objExists(node):
            err = "Guide does not exist: '{node}'".format(node=node)
            raise RuntimeError(err)
        return func(*args, **kwargs)
    locals = sys._getframe(1).f_locals
    name = wraps.__name__
    prop = locals.get(name)
    if not isinstance(prop, property):
        prop = property(wraps, doc=func.__doc__)
    else:
        doc = prop.__doc__ or func.__doc__
        prop = property(wraps, prop.fset, prop.fdel, doc)
    return prop


class HandleModel(ModuleModelDynamicBase):
    """Control handle to drive rig components
    """

    SUFFIX = "ctl"
    DEFAULT_STYLE = "circle"
    DEFAULT_COLOR = "yellow"

    def __init__(self, position, primary, primary_index, secondary,
                 secondary_index):
        super(HandleModel, self).__init__(position, primary, primary_index,
                                          secondary, secondary_index)

        self.__cvs = []

    @property
    def shapes(self):
        return self._dag.get("shapes", [])

    @property
    def handle(self):
        # TODO:
        #   This is bad, build this class better
        return str(self.name)

    @property
    def offset(self):
        return self._dag.get("offset")

    @property
    def group(self):
        return self._dag.get("group")

    @property
    def style(self):
        return self._meta.get("style", HandleModel.DEFAULT_STYLE)

    @property
    def color(self):
        return self._meta.get("color", HandleModel.DEFAULT_COLOR)

    def set_style(self, style):
        """Update stlye of handle.
        """
        self.store("style", style, container="meta")
        self.__cvs = get_cvs(style)
        self.__rebuild()

    def set_color(self, color):
        """Update color of handle
        """
        self.store("color", color, container="meta")
        self.__rebuild()

    def __create_offset(self):
        """
        """
        suffix = "{0}Offset".format(self.name.suffix)
        offset_name = name.rename(self.name, suffix=suffix)
        offset_node = cmds.createNode("transform", name=offset_name)
        self.store("offset", offset_node)
        cmds.parent(self.node, offset_node)

    def __create_group(self):
        """
        """
        suffix = "{0}Grp".format(self.name.suffix)
        group_name = name.rename(self.name, suffix=suffix)
        group_node = cmds.createNode("transform", name=group_name)
        self.store("group", group_node)
        cmds.parent(self.offset, group_node)

    def _create(self):
        with libmaya.Selection():
            self.__create_offset()
            self.__create_group()
            self.set_style(self.style)
            self.set_color(self.color)
            self.__attributes()

    def __rebuild(self):
        """Rebuild control handle shapes and colors
        """
        if self.exists:
            if self.shapes:
                cmds.delete(self.shapes)
            self.__create_shapes()
            for shape in self.shapes:
                libattr.set(shape, "overrideEnabled", 1)
                libattr.set(shape, "overrideColor", get_color(self.color))
            # self._refresh("dag")
            # self._refresh("nondag")
            # self._refresh("meta")
        return self

    def __attributes(self):
        libattr.lock_visibility(self.node)

    def __create_shapes(self):
        """Create shapes under control handle.
        """

        for crv in self.__cvs:
            degree = 1
            temp_curve = cmds.curve(name="temp_curve", d=degree, p=crv)
            shapes = cmds.listRelatives(temp_curve, shapes=True)
            for shape in shapes:
                cmds.parent(shape, self.node, shape=True, r=True)
            cmds.delete(temp_curve)

        # Rename
        shapes = cmds.listRelatives(self.node, shapes=True) or []
        for index, shape in enumerate(shapes):
            shape_name = name.rename(self.name, shape=True)
            cmds.rename(shape, shape_name)
            shapes[shapes.index(shape)] = shape_name
        self.store("shapes", shapes, container="dag")
