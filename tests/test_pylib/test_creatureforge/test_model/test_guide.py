#!/usr/bin/env /Applications/Autodesk/maya2016/Maya.app/Contents/bin/mayapy

import unittest

from maya import cmds

from creatureforge.model.guide import Up
from creatureforge.model.guide import Guide
from creatureforge.model.guide import Tendon


class TestGuide(unittest.TestCase):

    def setUp(self):
        cmds.file(new=True, force=True)

    def tearDown(self):
        pass

    def test_create(self):
        """Create guide and check exists in Maya context"""

        g = Guide("L", "arm", 0)
        g.create()
        self.assertEquals(cmds.objExists(g.node), True)

    def test_name(self):
        """Naming conventions and tokens"""

        g = Guide("L", "arm", 0)
        g.create()

        # Check tokens
        self.assertEquals(g.position, "L")
        self.assertEquals(g.description, "arm")
        self.assertEquals(g.index, 0)
        self.assertEquals(g.suffix, Guide.SUFFIX)

    def test_aim(self):
        """Aim transform exists
        """

        g = Guide("L", "arm", 0)
        self.assertIsNone(g.aim)

        g.create()
        self.assertEquals(cmds.objExists(g.aim), True)

    def test_up(self):
        """Up node exists
        """

        g = Guide("L", "arm", 0)
        self.assertIsNone(g.up)

        g.create()
        self.assertEquals(cmds.objExists(g.up.node), True)
        self.assertIsInstance(g.up, Up)

    def test_tendons(self):
        """Tendons are created
        """

        arm = Guide("L", "arm", 0)
        self.assertIsInstance(arm.tendons, tuple)
        self.assertEquals(len(arm.tendons), 0)

        arm.create()
        wrist = Guide("L", "wrist", 0)
        wrist.create()

        wrist.set_parent(arm)
        self.assertEquals(len(arm.tendons), 1)
        self.assertIsInstance(arm.tendons[0], Tendon)

    def test_setup(self):
        """Setup transform exists
        """

        g = Guide("L", "arm", 0)
        self.assertIsNone(g.setup)

        g.create()
        self.assertEquals(cmds.objExists(g.setup), True)

    def test_shapes(self):
        """Shapes exists under guide
        """

        g = Guide("L", "arm", 0)
        self.assertIsInstance(g.shapes, tuple)
        self.assertEquals(len(g.shapes), 0)

        g.create()
        for shape in g.shapes:
            self.assertEquals(cmds.objExists(shape), True)

    def test_constraint(self):
        """Aim constraint node exists
        """

        g = Guide("L", "arm", 0)
        self.assertIsNone(g.constraint)

        g.create()
        self.assertEquals(cmds.objExists(g.constraint), True)

    def test_condition(self):
        """Aim condition node exists
        """

        g = Guide("L", "arm", 0)
        self.assertIsNone(g.condition)

        g.create()
        self.assertEquals(cmds.objExists(g.condition), True)

    def test_parent(self):
        """Guide has parent
        """

        arm = Guide("L", "arm", 0)
        arm.create()

        self.assertIsNone(arm.parent)

        wrist = Guide("L", "wrist", 0)
        wrist.create()
        wrist.set_parent(arm)
        self.assertIsInstance(wrist.parent, Guide)
        self.assertEquals(wrist.parent, arm)

    def test_children(self):
        """Guide has children
        """

        arm = Guide("L", "arm", 0)
        arm.create()

        self.assertIsInstance(arm.children, tuple)
        self.assertEquals(len(arm.children), 0)

        wrist = Guide("L", "wrist", 0)
        wrist.create()
        wrist.set_parent(arm)
        self.assertIsInstance(arm.children[0], Guide)
        self.assertEquals(arm.children[0], wrist)
        self.assertEquals(len(arm.children), 1)

    def test_primary_aim(self):
        """Primary aim axis
        """

        order = Guide.ORIENT
        default_aim = order.keys()[0]

        arm = Guide("L", "arm", 0)
        self.assertIsNone(arm.primary)

        arm.create()
        self.assertEquals(arm.primary, default_aim[0].upper())

    def test_secondary_aim(self):
        """Secondary aim axis
        """

        order = Guide.ORIENT
        default_aim = order.keys()[0]

        arm = Guide("L", "arm", 0)
        self.assertIsNone(arm.secondary)

        arm.create()
        self.assertEquals(arm.secondary, default_aim[1].upper())
