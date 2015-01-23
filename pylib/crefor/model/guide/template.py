#!/usr/bin/env python

"""
Template model
"""

import time
import json
from maya import cmds

from collections import OrderedDict
from crefor.lib import libName

from crefor.model.guide.guide import Guide

from crefor import log
logger = log.get_logger(__name__)

__all__ = ["Template"]

class Template(object):
    """
    """

    def __init__(self, guides):

        self.__guides = [Guide.validate(g) for g in guides]

    def create(self):
        pass

    @property
    def nodes(self):
        """
        """

        return [g.node for g in self.__guides]

    @property
    def guides(self):
        """
        """

        return self.__guides

    def exists(self):
        """
        """

        return all([g.exists() for g in self.__guides])

    def compile(self):
        """
        """

        if not self.exists():
            raise RuntimeError("Cannot compile, one or more guides guides do not exist: %s" % self.nodes)

        guides = self.__guides

        # Create hierarchy
        hierarchy = {}
        for guide in guides:
            hierarchy[guide] = guide.children

        # Create joints
        joints = {}
        for guide in hierarchy:
            joint = guide.compile()
            joints[guide] = joint

        # Create joint hierarchy
        for guide in joints:
            for child in hierarchy[guide]:
                cmds.parent(joints[child], joints[guide])

        # Remove guides
        for guide in guides:
            guide.remove()

        return joints.values()

