#!/usr/bin/env python

"""
"""

import time
import logging
from collections import OrderedDict

from maya import cmds

from creatureforge.lib import libname
from creatureforge.lib import libattr
from creatureforge.lib import libutil
from creatureforge.lib import libconstraint
from creatureforge.decorators import Memoized
from creatureforge.model.base import Module
from creatureforge.exceptions import DuplicateNameError
from creatureforge.exceptions import GuideDoesNotExistError
from creatureforge.exceptions import GuideHierarchyError


class GuideError(Exception):
    pass

logger = logging.getLogger(__name__)

AXIS = ["X", "Y", "Z"]


def cache(func):
    def wraps(*args, **kwargs):
        node = args[0].node
        if not cmds.objExists(node):
            err = "Guide does not exist: '{node}'".format(node=node)
            raise RuntimeError(err)
        return func(*args, **kwargs)
    return wraps


class Up(Module):

    SUFFIX = "up"
    RAIDUS = 0.3

    def __init__(self, guide):

        self.__guide = guide

        super(Up, self).__init__(*guide.tokens)

    @cache
    def get_translates(self, worldspace=True):
        return tuple(cmds.xform(self.get_node(), q=True, ws=worldspace, t=True))

    @cache
    def set_translates(self, x, y, z, worldspace=False):
        logger.debug("Setting {node} position: ({x}, {y}, {z})".format(
            node=self.get_node(), x=x, y=y, z=z))
        cmds.xform(self.get_node(), ws=worldspace, t=[x, y, z])

    @cache
    def get_guide(self):
        return self.__guide

    @cache
    def get_group(self):
        return self._dag.get("grp")

    @cache
    def get_shapes(self):
        return self._dag.get("shapes")

    def __create_node(self):
        grp_name = libname.rename(self.get_name().compile(), append="Up", suffix="grp")
        grp = cmds.createNode("transform", name=grp_name)
        self.store("grp", grp)

        sphere = cmds.sphere(name=self.get_name().compile(), radius=Up.RAIDUS)[0]
        shapes = cmds.listRelatives(sphere, shapes=True)

        cmds.parent(sphere, grp)

        # Add attributes
        libattr.add_double(self.get_node(), "guideScale", min=0.01, dv=1)

        for attr in ["guideScale"]:
            libattr.set(self.get_node(), attr, keyable=False, channelBox=True)

        guide = self.get_guide()
        for axis in AXIS:
            cmds.connectAttr("{node}.guideScale".format(node=guide.node),
                             "{grp}.scale{axis}".format(grp=grp, axis=axis))

        self.store("node", sphere)
        self.store("shapes", shapes, append=shapes)

    def __create_scale(self):
        shapes = self.get_shapes()
        cl, cl_handle = cmds.cluster(shapes)
        libattr.set(cl, "relative", True)
        cl_handle = cmds.rename(cl_handle, libname.rename(self.get_node(), append="upScale", suffix="clh"))
        self.store("scale", cl_handle)

        for axis in AXIS:
            cmds.connectAttr("{node}.guideScale".format(node=self.get_node()),
                             "{handle}.scale{axis}".format(handle=cl_handle, axis=axis))

        group = self.get_group()
        cmds.parent(cl_handle, group)

    def _create(self):
        self.__create_node()
        self.__create_scale()

        libattr.set(self.get_node(), "translateY", 3)

    def _post(self):
        super(Up, self)._post()

        # Lock up some attributes
        libattr.lock_rotate(self.get_node())
        libattr.lock_scale(self.get_node())
        libattr.lock_visibility(self.get_node())
