#!/usr/bin/env python

"""
"""

import json
from collections import OrderedDict
from copy import deepcopy

from creatureforge.lib import libattr
from creatureforge.model.base import Module
from creatureforge.model.base import ModuleModelBase

from maya import cmds


class BipedBuild(ModuleModelBase):

    SUFFIX = "rig"

    def __init__(self, *args, **kwargs):
        super(BipedBuild, self).__init__(*args, **kwargs)

    def __create_node(self):
        cmds.createNode("transform", name=self.get_name())

    def __create_guide_system(self):
        raise NotImplementedError("Add me!!")

    def _create(self):
        self.__create_node()
        self.__create_guide_system()
