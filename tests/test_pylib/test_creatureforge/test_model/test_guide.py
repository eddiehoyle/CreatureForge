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

    def tearDown(self):
        pass

    def test_create(self):
        """[model.guide.Guide.create]
        Create guide and check exists in Maya context
        """

        arm = Guide(POSITION, DESCRIPTION, index=INDEX)

        with self.assertRaises(Exception):
            arm.get_node()

        self.assertEquals(arm.exists(), False)

        arm.create()
        node = arm.get_node()
        self.assertEquals(cmds.objExists(node), True)

        self.assertEquals(arm.exists(), True)

    def test_aim(self):
        """[model.guide.Guide.aim]
        Aim transform exists
        """

        arm = Guide(POSITION, DESCRIPTION, index=INDEX)

        with self.assertRaises(Exception):
            arm.get_aim()

        arm.create()
        aim = arm.get_aim()
        self.assertEquals(cmds.objExists(aim), True)

    def test_up(self):
        """[model.guide.Guide.up]
        Up node exists
        """

        arm = Guide(POSITION, DESCRIPTION, index=INDEX)

        with self.assertRaises(Exception):
            arm.get_aim()

        arm.create()
        aim = arm.get_aim()
        self.assertEquals(cmds.objExists(aim), True)

    def test_setup(self):
        """[model.guide.Guide.setup]
        Setup transform exists
        """

        arm = Guide(POSITION, DESCRIPTION, index=INDEX)

        with self.assertRaises(Exception):
            arm.get_setup()

        arm.create()
        setup = arm.get_setup()
        self.assertEquals(cmds.objExists(setup), True)

    def test_shapes(self):
        """[model.guide.Guide.shapes]
        Shapes exists under guide
        """

        arm = Guide(POSITION, DESCRIPTION, index=INDEX)

        with self.assertRaises(Exception):
            arm.get_shapes()

        arm.create()
        shapes = arm.get_shapes()
        for shape in shapes:
            self.assertEquals(cmds.objExists(shape), True)

    def test_constraint(self):
        """[model.guide.Guide.aim]
        Aim constraint node exists
        """

        arm = Guide(POSITION, DESCRIPTION, index=INDEX)

        with self.assertRaises(Exception):
            arm.get_constraint()

        arm.create()
        constraint = arm.get_constraint()
        self.assertEquals(cmds.objExists(constraint), True)

    def test_condition(self):
        """[model.guide.Guide.condition]
        Aim condition node exists
        """

        arm = Guide(POSITION, DESCRIPTION, index=INDEX)

        with self.assertRaises(Exception):
            arm.get_condition()

        arm.create()
        condition = arm.get_condition()
        self.assertEquals(cmds.objExists(condition), True)

    def test_parent(self):
        """[model.guide.Guide.parent]
        Guide has parent
        """

        arm = Guide(POSITION, DESCRIPTION, index=INDEX)

        with self.assertRaises(Exception):
            arm.get_parent()

        arm.create()
        parent = arm.get_parent()
        self.assertIsNone(parent)

    def test_children(self):
        """[model.guide.Guide.children]
        Guide has children
        """

        arm = Guide(POSITION, DESCRIPTION, index=INDEX)

        with self.assertRaises(Exception):
            arm.get_children()

        arm.create()
        children = arm.get_children()
        self.assertIsInstance(children, tuple)
        self.assertEquals(len(children), 0)

    def test_get_aim_at(self):
        """[model.guide.Guide.get_aim_at]
        Get which guide parent guide is aiming at
        """

        arm = Guide(POSITION, DESCRIPTION, index=INDEX)

        with self.assertRaises(Exception):
            arm.get_aim_at()

        arm.create()

        aim_at = arm.get_aim_at()
        self.assertIsNone(aim_at)

    def test_get_aim_orient(self):
        """[model.guide.Guide.get_aim_orient]
        Get guide aim orient
        """

        arm = Guide(POSITION, DESCRIPTION, index=INDEX)

        with self.assertRaises(Exception):
            arm.get_aim_orient()

        arm.create()

        aim_orient = arm.get_aim_orient()
        self.assertIsInstance(aim_orient, tuple)
        self.assertEquals(len(aim_orient), 3)

    def test_get_offset_orient(self):
        """[model.guide.Guide.get_offset_orient]
        Get guide offset orient """

        arm = Guide(POSITION, DESCRIPTION, index=INDEX)

        with self.assertRaises(Exception):
            arm.get_offset_orient()

        arm.create()

        offset_orient = arm.get_offset_orient()
        self.assertIsInstance(offset_orient, tuple)
        self.assertEquals(len(offset_orient), 3)

    def test_get_translates(self):
        """[model.guide.Guide.get_translates]
        Get translates
        """

        arm = Guide(POSITION, DESCRIPTION, index=INDEX)

        with self.assertRaises(Exception):
            arm.get_translates()

        arm.create()
        self.assertEquals(arm.get_translates(), (0, 0, 0))

        translates = (0, 3, 0)
        arm.set_translates(*translates)
        self.assertEquals(arm.get_translates(), translates)

    def test_set_translates(self):
        """[model.guide.Guide.set_translates]
        """

        arm = Guide(POSITION, DESCRIPTION, index=INDEX)
        arm.create()

        translates = (0, 3, 0)
        arm.set_translates(*translates)
        self.assertEquals(arm.get_translates(), translates)

    def test_copy(self):
        """[model.guide.copyGuide.]
        """

        arm = Guide(POSITION, DESCRIPTION, index=INDEX)
        arm.create()

        new = arm.copy()

        index = new.get_name().index
        self.assertEquals(index - 1, INDEX)

    def test_remove(self):
        """[model.Guide.remove.guide]
        """

        arm = Guide(POSITION, DESCRIPTION, index=INDEX)
        arm.create()

        dag = arm.get_dag()
        nondag = arm.get_nondag()
        arm.remove()

        for data in [dag, nondag]:
            for key, value in dag.iteritems():
                if not isinstance(value, (tuple, list, set)):
                    value = [value]
                for node in value:
                    self.assertEquals(cmds.objExists(node), False)


    # def test_remove_parent(self):
    #     """[model.guide.Guide.remove_parent]
    #     """
    #     raise NotImplementedError()

    # def test_remove_child(self):
    #     """[model.guide.Guide.remove_child]
    #     """
    #     raise NotImplementedError()

    # def test_get_snapshot(self):
    #     """[model.guide.Guide.get_snapshot]
    #     """
    #     raise NotImplementedError()
