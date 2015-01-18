#!/usr/bin/env python

"""
"""

from maya import cmds
from crefor.model.guide.guide import Guide
from crefor.lib import libName

import unittest

class TestUp(unittest.TestCase):
    """
    Test connectors between two guides
    """

    def __create(self):
        arm = Guide("L", "arm", 0)
        arm.create()

        return arm.up

    def setUp(self):
        """Runs before each test"""
        cmds.file(newFile=True, force=True)

    def tearDown(self):
        """Runs after each test"""
        pass

    def test_create(self):
        """
        Test create()
        """

        up = self.__create()

        self.assertEquals(cmds.objExists(up.node),
                          True,
                          "Up does not exist: %s" % up.node)

        for key, nodes in up.nodes.items():
            if not isinstance(nodes, list):
                nodes = [nodes]
            for node in nodes:
                self.assertEquals(cmds.objExists(node),
                                  True,
                                  "Node does not exist: %s" % node)