#!/usr/bin/env python

"""
"""

import json
from collections import OrderedDict
from copy import deepcopy

from creatureforge.lib import libattr
from creatureforge.build._base import BuildBase
from creatureforge.control import name
from creatureforge.model.components.skeleton import ComponentSkeletonModel

from maya import cmds


class BipedBuild(BuildBase):

    SUFFIX = "rig"

    def __init__(self, *args, **kwargs):
        super(BipedBuild, self).__init__(*args, **kwargs)

        self.skeleton = None

    def _new(self):
        cmds.file(new=True, force=True)

    def _create_node(self):
        node = cmds.createNode("transform", name=self.name)
        libattr.lock_all(node)

    def _create_skeleton(self):
        skeleton_name = name.rename(self.name, secondary="skeleton")
        skeleton = ComponentSkeletonModel(*skeleton_name.tokens)
        path = "/Users/eddiehoyle/Documents/maya/projects/fishy/scenes/skeleton.mb"
        skeleton.set_path(path)
        skeleton.create()
        cmds.parent(skeleton.node, self.node)
        self.skeleton = skeleton

    def _create(self):
        self._new()
        self._create_node()
        self._create_skeleton()
