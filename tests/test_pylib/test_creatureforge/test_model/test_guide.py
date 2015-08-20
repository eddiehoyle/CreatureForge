#!/usr/bin/env /Applications/Autodesk/maya2016/Maya.app/Contents/bin/mayapy

import unittest

from maya import cmds

from creatureforge.model.guide import Up
from creatureforge.model.guide import Guide
from creatureforge.model.guide import Tendon

# ------------------------------------------------------------------------------

POSITION = "L"
DESCRIPTION = "arm"
INDEX = 0

def generate(count):
    guides = []
    while count:
        guide = Guide(POSITION, DESCRIPTION, index=count)
        guide.create()
        guides.append(guide)
        count -= 1
    return guides

# ------------------------------------------------------------------------------

class TestGuide(unittest.TestCase):

    def setUp(self):
        cmds.file(new=True, force=True)
        Guide(POSITION, DESCRIPTION, index=INDEX).create()

    def tearDown(self):
        pass

    def test_create(self):
        """[model.guide.Guide.create]
        Create guide and check exists in Maya context
        """

        g = Guide(POSITION, DESCRIPTION, index=INDEX)
        g.create()
        self.assertEquals(cmds.objExists(g.node), True)

    def test_node(self):
        """[model.guide.Guide.node]
        Naming conventions and tokens
        """

        g = Guide(POSITION, DESCRIPTION, index=INDEX)
        g.create()

        # Check tokens
        self.assertEquals(g.position, POSITION)
        self.assertEquals(g.description, DESCRIPTION)
        self.assertEquals(g.index, 0)
        self.assertEquals(g.suffix, Guide.SUFFIX)

    def test_aim(self):
        """[model.guide.Guide.aim]
        Aim transform exists
        """

        g = Guide(POSITION, DESCRIPTION, index=INDEX)
        self.assertIsNone(g.aim)

        g.create()
        self.assertEquals(cmds.objExists(g.aim), True)

    def test_up(self):
        """[model.guide.Guide.up]
        Up node exists
        """

        g = Guide(POSITION, DESCRIPTION, index=INDEX)
        self.assertIsNone(g.up)

        g.create()
        self.assertEquals(cmds.objExists(g.up.node), True)
        self.assertIsInstance(g.up, Up)

    def test_tendons(self):
        """[model.guide.Guide.tendons]
        Tendons are created
        """

        arm = Guide(POSITION, DESCRIPTION, index=INDEX)
        self.assertIsInstance(arm.tendons, tuple)
        self.assertEquals(len(arm.tendons), 0)

        arm.create()
        wrist = Guide("L", "wrist", 0)
        wrist.create()

        wrist.set_parent(arm)
        self.assertEquals(len(arm.tendons), 1)
        self.assertIsInstance(arm.tendons[0], Tendon)

    def test_setup(self):
        """[model.guide.Guide.setup]
        Setup transform exists
        """

        g = Guide(POSITION, DESCRIPTION, index=INDEX)
        self.assertIsNone(g.setup)

        g.create()
        self.assertEquals(cmds.objExists(g.setup), True)

    def test_shapes(self):
        """[model.guide.Guide.shapes]
        Shapes exists under guide
        """

        g = Guide(POSITION, DESCRIPTION, index=INDEX)
        self.assertIsInstance(g.shapes, tuple)
        self.assertEquals(len(g.shapes), 0)

        g.create()
        for shape in g.shapes:
            self.assertEquals(cmds.objExists(shape), True)

    def test_constraint(self):
        """[model.guide.Guide.aim]
        Aim constraint node exists
        """

        g = Guide(POSITION, DESCRIPTION, index=INDEX)
        self.assertIsNone(g.constraint)

        g.create()
        self.assertEquals(cmds.objExists(g.constraint), True)

    def test_condition(self):
        """[model.guide.Guide.condition]
        Aim condition node exists
        """

        g = Guide(POSITION, DESCRIPTION, index=INDEX)
        self.assertIsNone(g.condition)

        g.create()
        self.assertEquals(cmds.objExists(g.condition), True)

    def test_parent(self):
        """[model.guide.Guide.parent]
        Guide has parent
        """

        arm = Guide(POSITION, DESCRIPTION, index=INDEX)
        arm.create()

        self.assertIsNone(arm.parent)

        wrist = Guide("L", "wrist", 0)
        wrist.create()
        wrist.set_parent(arm)
        self.assertIsInstance(wrist.parent, Guide)
        self.assertEquals(wrist.parent, arm)

    def test_children(self):
        """[model.guide.Guide.children]
        Guide has children
        """

        arm = Guide(POSITION, DESCRIPTION, index=INDEX)
        arm.create()

        self.assertIsInstance(arm.children, tuple)
        self.assertEquals(len(arm.children), 0)

        wrist = Guide("L", "wrist", 0)
        wrist.create()
        wrist.set_parent(arm)
        self.assertIsInstance(arm.children[0], Guide)
        self.assertEquals(arm.children[0], wrist)
        self.assertEquals(len(arm.children), 1)

    def test_get_aim_at(self):
        """[model.guide.Guide.get_aim_at]
        Get which guide parent guide is aiming at
        """
        raise NotImplementedError()

    def test_get_aim_orient(self):
        """[model.guide.Guide.get_aim_orient]
        Get guide aim orient
        """
        raise NotImplementedError()

    def test_get_offset_orient(self):
        """[model.guide.Guide.get_offset_orient]
        Get guide offset orient """
        raise NotImplementedError()

    def test_get_translates(self):
        """[model.guide.Guide.get_translates]
        Get translates
        """
        raise NotImplementedError()

    def test_set_translates(self):
        """[model.guide.Guide.set_translates]
        """
        raise NotImplementedError()

    def test_copy(self):
        """[model.guide.copyGuide.]
        """
        raise NotImplementedError()

    def test_has_parent(self):
        """[model.guide.Guide.has_parent]
        """
        raise NotImplementedError()

    def test_has_child(self):
        """[model.guide.Guide.has_child]
        """
        raise NotImplementedError()

    def test_set_parent(self):
        """[model.guide.Guide.set_parent]
        """
        raise NotImplementedError()

    def test_add_child(self):
        """[model.guide.add_childGuide.]
        """
        raise NotImplementedError()

    def test_remove(self):
        """[model.Guide.remove.guide]
        """
        raise NotImplementedError()

    def test_remove_parent(self):
        """[model.guide.Guide.remove_parent]
        """
        raise NotImplementedError()

    def test_remove_child(self):
        """[model.guide.Guide.remove_child]
        """
        raise NotImplementedError()

    def test_get_snapshot(self):
        """[model.guide.Guide.get_snapshot]
        """
        raise NotImplementedError()
