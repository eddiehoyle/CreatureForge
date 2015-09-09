#!/usr/bin/env /Applications/Autodesk/maya2016/Maya.app/Contents/bin/mayapy

import unittest

from maya import cmds

from creatureforge.model.up import UpModel
from creatureforge.model.guide import GuideModel

# ------------------------------------------------------------------------------

POSITION = "L"
PRIMARY = "arm"
PRIMARY_INDEX = 0
SECONDARY = "wrist"
SECONDARY_INDEX = 0

# ------------------------------------------------------------------------------

def create_arm():
    guide = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, SECONDARY, SECONDARY_INDEX)
    guide.create()
    return guide

def create_wrist():
    guide = GuideModel(POSITION, "wrist", PRIMARY_INDEX, SECONDARY, SECONDARY_INDEX)
    guide.create()
    return guide

# ------------------------------------------------------------------------------

class TestGuideModel(unittest.TestCase):

    def setUp(self):
        cmds.file(new=True, force=True)

    def tearDown(self):
        pass

    def test_create(self):
        """[model.guide.GuideModel.create]
        Create guide and check exists in Maya context
        """

        arm = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, SECONDARY, SECONDARY_INDEX)

        with self.assertRaises(Exception):
            arm.get_node()

        self.assertEquals(arm.exists(), False)

        arm.create()

        # Can't create twice
        with self.assertRaises(Exception):
            arm.create()

        node = arm.get_node()
        self.assertEquals(cmds.objExists(node), True)

        self.assertEquals(arm.exists(), True)

    def test_get_aim(self):
        """[model.guide.GuideModel.get_aim]
        Aim transform exists
        """

        arm = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, SECONDARY, SECONDARY_INDEX)

        with self.assertRaises(Exception):
            arm.get_aim()

        arm.create()
        aim = arm.get_aim()
        self.assertEquals(cmds.objExists(aim), True)

    def test_get_up(self):
        """[model.guide.GuideModel.get_up]
        UpModel node exists
        """

        arm = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, SECONDARY, SECONDARY_INDEX)

        with self.assertRaises(Exception):
            arm.get_up()

        arm.create()
        up = arm.get_up()
        self.assertEquals(cmds.objExists(up.get_node()), True)

    def test_get_setup(self):
        """[model.guide.GuideModel.get_setup]
        Setup transform exists
        """

        arm = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, SECONDARY, SECONDARY_INDEX)

        with self.assertRaises(Exception):
            arm.get_setup()

        arm.create()
        setup = arm.get_setup()
        self.assertEquals(cmds.objExists(setup), True)

    def test_get_shapes(self):
        """[model.guide.GuideModel.get_shapes]
        Shapes exists under guide
        """

        arm = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, SECONDARY, SECONDARY_INDEX)

        with self.assertRaises(Exception):
            arm.get_shapes()

        arm.create()
        shapes = arm.get_shapes()
        for shape in shapes:
            self.assertEquals(cmds.objExists(shape), True)

    def test_get_constraint(self):
        """[model.guide.GuideModel.get_constraint]
        Aim constraint node exists
        """

        arm = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, SECONDARY, SECONDARY_INDEX)

        with self.assertRaises(Exception):
            arm.get_constraint()

        arm.create()
        constraint = arm.get_constraint()
        self.assertEquals(cmds.objExists(constraint), True)

    def test_get_condition(self):
        """[model.guide.GuideModel.get_condition]
        Aim condition node exists
        """

        arm = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, SECONDARY, SECONDARY_INDEX)

        with self.assertRaises(Exception):
            arm.get_condition()

        arm.create()
        condition = arm.get_condition()
        self.assertEquals(cmds.objExists(condition), True)

    def test_get_parent(self):
        """[model.guide.GuideModel.get_parent]
        Get GuideModel parent
        """

        arm = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, SECONDARY, SECONDARY_INDEX)

        with self.assertRaises(Exception):
            arm.get_parent()

        arm.create()
        parent = arm.get_parent()
        self.assertIsNone(parent)

    def test_get_children(self):
        """[model.guide.GuideModel.get_children]
        GuideModel has children
        """

        arm = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, SECONDARY, SECONDARY_INDEX)

        with self.assertRaises(Exception):
            arm.get_children()

        arm.create()
        children = arm.get_children()
        self.assertIsInstance(children, tuple)
        self.assertEquals(len(children), 0)

    def test_get_aim_at(self):
        """[model.guide.GuideModel.get_aim_at]
        Get which guide parent guide is aiming at
        """

        arm = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, SECONDARY, SECONDARY_INDEX)

        with self.assertRaises(Exception):
            arm.get_aim_at()

        arm.create()

        aim_at = arm.get_aim_at()
        self.assertIsNone(aim_at)

    def test_get_aim_orient(self):
        """[model.guide.GuideModel.get_aim_orient]
        Get guide aim orient
        """

        arm = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, SECONDARY, SECONDARY_INDEX)

        with self.assertRaises(Exception):
            arm.get_aim_orient()

        arm.create()

        aim_orient = arm.get_aim_orient()
        self.assertIsInstance(aim_orient, str)
        self.assertEquals(len(aim_orient), 3)

    def test_get_offset_orient(self):
        """[model.guide.GuideModel.get_offset_orient]
        Get guide offset orient """

        arm = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, SECONDARY, SECONDARY_INDEX)

        with self.assertRaises(Exception):
            arm.get_offset_orient()

        arm.create()

        offset_orient = arm.get_offset_orient()
        self.assertIsInstance(offset_orient, tuple)
        self.assertEquals(len(offset_orient), 3)

    def test_get_translates(self):
        """[model.guide.GuideModel.get_translates]
        Get translates
        """

        arm = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, SECONDARY, SECONDARY_INDEX)

        with self.assertRaises(Exception):
            arm.get_translates()

        arm.create()
        self.assertEquals(arm.get_translates(), (0, 0, 0))

        translates = (0, 3, 0)
        arm.set_translates(*translates)
        self.assertEquals(arm.get_translates(), translates)

    def test_set_translates(self):
        """[model.guide.GuideModel.set_translates]
        """

        arm = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, SECONDARY, SECONDARY_INDEX)
        arm.create()

        translates = (0, 3, 0)
        arm.set_translates(*translates)
        self.assertEquals(arm.get_translates(), translates)

    def test_copy(self):
        """[model.guide.GuideModel.copy]
        """

        arm = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, SECONDARY, SECONDARY_INDEX)
        arm.create()

        # TODO
        #   Generate primary or secondary or both
        new = arm.copy()

        primary_index = new.get_name().primary_index
        self.assertEquals(primary_index - 1, PRIMARY_INDEX)

    def test_remove(self):
        """[model.guide.GuideModel.remove]
        """

        arm = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, SECONDARY, SECONDARY_INDEX)

        with self.assertRaises(Exception):
            arm.remove()

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

    def test_get_snapshot(self):
        """[model.guide.GuideModel.get_snapshot]
        GuideModel snapshot is created with correct data
        """

        arm = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, SECONDARY, SECONDARY_INDEX)

        with self.assertRaises(Exception):
            arm.get_snapshot()

        arm.create()

        snapshot = arm.get_snapshot()

        self.assertEquals(snapshot["node"], arm.get_node())
        self.assertEquals(snapshot["parent"], arm.get_parent())
        self.assertEquals(snapshot["children"], arm.get_children())
        self.assertEquals(snapshot["aim_orient"], arm.get_aim_orient())
        self.assertEquals(snapshot["offset_orient"], arm.get_offset_orient())
        self.assertEquals(snapshot["aim_at"], arm.get_aim_at())
        self.assertEquals(snapshot["aim_flip"], arm.get_aim_flip())
        self.assertEquals(snapshot["translates"], arm.get_translates())
        self.assertEquals(snapshot["up_translates"], arm.get_up().get_translates())

    def test_compile(self):
        """[model.guide.GuideModel.compile]
        GuideModel compiles to joint
        """

        arm = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, SECONDARY, SECONDARY_INDEX)

        with self.assertRaises(Exception):
            arm.compile()

        arm.create()
        joint = arm.compile()
        self.assertEquals(cmds.objExists(joint), True)


class TestGuideModelHierarchy(unittest.TestCase):

    def setUp(self):
        cmds.file(new=True, force=True)

    def tearDown(self):
        pass

    def test_get_parent(self):
        """[model.guide.GuideModel.get_parent]
        GuideModel get parent
        """

        elbow = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, "elbow", 0)

        with self.assertRaises(Exception):
            elbow.get_parent()

        elbow.create()

        wrist = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, "wrist", 0)
        wrist.create()

        wrist.set_parent(elbow)

        self.assertEquals(wrist.get_parent(), elbow)

    def test_get_children(self):
        """[model.guide.GuideModel.get_children]
        GuideModel get children
        """

        elbow = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, "elbow", 0)

        with self.assertRaises(Exception):
            elbow.get_children()

        elbow.create()

        wrist = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, "wrist", 0)
        wrist.create()

        wrist.set_parent(elbow)

        self.assertEquals(wrist in elbow.get_children(), True)

    def test_get_aim_at(self):
        """[model.guide.GuideModel.get_aim_at]
        GuideModel is aiming at child
        """
        arm = create_arm()
        wrist = create_wrist()

        wrist.set_parent(arm)

        self.assertEquals(arm.get_aim_at(), wrist.get_node())

    def test_has_parent(self):
        """[model.guide.GuideModel.has_parent]
        GuideModel has parent anywhere above it
        """

        shoulder = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, "shoulder", 0)
        shoulder.create()

        elbow = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, "elbow", 0)

        with self.assertRaises(Exception):
            elbow.has_parent(shoulder)

        elbow.create()

        wrist = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, "wrist", 0)
        wrist.create()

        wrist.set_parent(elbow)
        elbow.set_parent(shoulder)

        self.assertEquals(wrist.has_parent(shoulder), True)


    def test_has_child(self):
        """[model.guide.GuideModel.has_child]
        GuideModel has child
        """

        shoulder = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, "shoulder", 0)
        shoulder.create()

        elbow = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, "elbow", 0)

        with self.assertRaises(Exception):
            elbow.has_child(shoulder)

        elbow.create()

        shoulder.add_child(elbow)

        self.assertEquals(shoulder.has_child(elbow), True)

    def test_set_parent(self):
        """[model.guide.GuideModel.set_parent]
        Set guide parent
        """

        shoulder = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, "shoulder", 0)
        shoulder.create()

        elbow = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, "elbow", 0)

        with self.assertRaises(Exception):
            elbow.set_parent(shoulder)

        elbow.create()
        elbow.set_parent(shoulder)
        self.assertEquals(elbow.get_parent(), shoulder)

    def test_add_child(self):
        """[model.guide.GuideModel.add_child]
        Add guide as a child
        """

        shoulder = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, "shoulder", 0)
        elbow = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, "elbow", 0)

        with self.assertRaises(Exception):
            shoulder.add_child(elbow)

        shoulder.create()
        elbow.create()

        shoulder.add_child(elbow)
        self.assertEquals(shoulder.get_child(elbow), elbow)

    def test_get_child(self):
        """[model.guide.GuideModel.get_child]
        GuideModel get child
        """

        shoulder = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, "shoulder", 0)
        elbow = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, "elbow", 0)

        with self.assertRaises(Exception):
            shoulder.get_child(elbow)

        shoulder.create()
        elbow.create()

        shoulder.add_child(elbow)
        self.assertEquals(shoulder.get_child(elbow), elbow)

    def test_remove_parent(self):
        """[model.guide.GuideModel.remove_parent]
        Remove parent guide
        """

        shoulder = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, "shoulder", 0)
        elbow = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, "elbow", 0)

        with self.assertRaises(Exception):
            shoulder.remove_parent()

        shoulder.create()
        elbow.create()

        parent = elbow.get_parent()

        elbow.set_parent(shoulder)
        elbow.remove_parent()

        self.assertEquals(parent, elbow.get_parent())

    def test_remove_child(self):
        """[model.guide.GuideModel.remove_child]
        Remove child guide
        """

        shoulder = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, "shoulder", 0)
        elbow = GuideModel(POSITION, PRIMARY, PRIMARY_INDEX, "elbow", 0)

        # Doesn't exist yet
        with self.assertRaises(Exception):
            shoulder.remove_child(elbow)

        shoulder.create()
        elbow.create()

        # Not connected yet
        with self.assertRaises(Exception):
            shoulder.remove_child(elbow)

        shoulder.add_child(elbow)
        shoulder.remove_child(elbow)

        self.assertEquals(elbow not in shoulder.get_children(), True)
