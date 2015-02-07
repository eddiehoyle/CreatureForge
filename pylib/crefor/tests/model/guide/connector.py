#!/usr/bin/env python

"""
"""

from maya import cmds
from crefor.model.guide import Guide
from crefor.lib import libName

import unittest

class TestConnector(unittest.TestCase):
    """
    Test connectors between two guides
    """

    def __create(self):
        arm = Guide("L", "arm", 0)
        arm.create()

        spine = Guide("C", "spine", 0)
        spine.create()

        arm.set_parent(spine)
        connectors = spine.connectors

        return arm, spine, connectors

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

        arm, spine, connectors = self.__create()

        self.assertEquals(arm.connectors == [],
                          True,
                          "Child appears to have connectors: %s" % arm.connectors)
        self.assertEquals(len(connectors),
                          1,
                          "Parent guide is missing connectors: %s" % connectors)

        # Test parent, child of connector
        self.assertEquals(connectors[0].parent == spine,
                          True,
                          "Connector parent is incorrect: %s" % connectors[0].parent)
        self.assertEquals(connectors[0].child == arm,
                          True,
                          "Connector child is incorrect: %s" % connectors[0].child)

    def test_remove(self):
        """
        Test remove()
        """

        arm, spine, connectors = self.__create()

        arm.remove()

        self.assertEquals(spine.connectors == [],
                          True,
                          "Parent still has connectors: %s" % spine.connectors)

        spine.remove()

        self.assertEquals(arm.connectors == [],
                          True,
                          "Child has connectors for some reason: %s" % arm.connectors)

    def test_node(self):
        """
        Test property nodes
        """

        arm, spine, connectors = self.__create()

        self.assertEquals(len(connectors[0].nodes) != 0,
                          True,
                          "Connector nodes returned empty list: %s" % connectors[0].nodes)

        for node in connectors[0].nodes.values():
            self.assertEquals(cmds.objExists(node), True,
                              "Node does not exist: %s" % node)


class TestConnectorReinit(TestConnector):
    """
    Repeat all tests but after being reinitialised from string
    """

    def __create(self):
        arm = Guide("L", "arm", 0)
        arm.create()

        spine = Guide("C", "spine", 0)
        spine.create()

        arm.set_parent(spine)

        arm = Guide(*libName.decompile(arm.node, 3)).reinit()
        spine = Guide(*libName.decompile(spine.node, 3)).reinit()
        connectors = spine.connectors

        return arm, spine, connectors
