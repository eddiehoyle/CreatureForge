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
from creatureforge.model.parts.base import PartModelBase


class FkError(Exception):
    pass

logger = logging.getLogger(__name__)


def cache(func):
    def wraps(*args, **kwargs):
        node = args[0].node
        if not cmds.objExists(node):
            err = "Guide does not exist: '{node}'".format(node=node)
            raise RuntimeError(err)
        return func(*args, **kwargs)
    return wraps


class FkModel(PartModelBase):

    def __init__(self, position, description, index=0):
        super(FkModel, self).__init__(position, description, index=index)

        self.__joints = []

    def get_joints(self):
        return tuple(self.__joints)

    def set_joints(self, joints):
        if self.exists():
            err = "Cannot set joints after part has been created!"
            raise RuntimeError(err)

        _joints = []
        for dag in joints:
            if cmds.nodeType(dag) == "joint":
                _joints.append(dag)

        logger.debug("Setting joints for '{name}': {joints}".format(
            name=self.get_name(), joints=_joints))
        self.__joints = _joints

    def _pre(self):
        if not self.get_joints():
            err = "Cannot create '{name}' as no joints have been set!".format(
                name=self.get_name().compile())
            raise ValueError(err)
        super(FkModel, self)._pre()

    def _create(self):
        self.__create_node()
        self.__create_setup()
        self.__create_control()

    def __create_node(self):
        name = libname.rename(self.get_name().compile(), suffix=FkModel.SUFFIX)
        cmds.createNode("transform", name=name)

    def __create_control(self):
        name = libname.rename(self.get_node(), suffix="control")
        control = cmds.createNode("transform", name=name)
        cmds.parent(control, self.get_node())
        self.store("control", control)

    def __create_setup(self):
        name = libname.rename(self.get_node(), suffix="setup")
        setup = cmds.createNode("transform", name=name)
        cmds.parent(setup, self.get_node())
        self.store("setup", setup)









