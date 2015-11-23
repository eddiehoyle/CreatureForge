#!/usr/bin/env python

"""
"""

import time
import logging
from collections import OrderedDict

from maya import cmds

from creatureforge.lib import libxform
from creatureforge.lib import libattr
from creatureforge.control import name
from creatureforge.control import handle
from creatureforge.model.components._base import ComponentModelBase


logger = logging.getLogger(__name__)


class ComponentSkeletonModel(ComponentModelBase):
    """
    A compiled skeleton component.
    """

    def __init__(self, position, primary, primary_index, secondary,
                 secondary_index):
        super(ComponentSkeletonModel, self).__init__(position, primary,
                                                     primary_index, secondary,
                                                     secondary_index)

        self.__path = None
        self.__joints = []

    def get_path(self):
        return self.__path

    def set_path(self, path):
        self.__path = path

    def _create_skeleton(self):
        before = cmds.ls(dag=True)
        cmds.file(self.get_path(), i=True)
        after = cmds.ls(dag=True)
        joints = list(set(after) - set(before))
        self.__joints = joints

    def _create_hierarchy(self):
        for node in self.get_joints():
            if not cmds.listRelatives(node, parent=True) or []:
                cmds.parent(node, self.setup)

    def _create(self):
        if not self.get_path():
            raise ValueError("Set skeleton path")

        self._create_skeleton()
        self._create_hierarchy()
