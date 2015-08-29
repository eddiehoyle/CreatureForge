#!/usr/bin/env /Applications/Autodesk/maya2016/Maya.app/Contents/bin/mayapy

import os
import tempfile
import unittest
from pprint import pprint

from maya import cmds

from creatureforge.control import guide
from creatureforge.model.guide import Guide


class TestControlGuide(unittest.TestCase):

    def setUp(self):
        cmds.file(new=True, force=True)

    def tearDown(self):
        pass

    def test_create(self):
        """[control.guide.create]
        Create guide and check exists in Maya context
        """

        arm = guide.create("L", "arm", index=0)
        self.assertEquals(cmds.objExists(arm.get_node()), True)
        self.assertIsInstance(arm, Guide)

    def test_get_hierarchy(self):
        """[control.guide.get_hierarchy]
        Get hierarchy of guide
        """

        elbow = guide.create("L", "elbow", index=0)
        wrist = guide.create("L", "wrist", index=0)

        data = guide.get_hierarchy(elbow)
        self.assertEquals(data.get(elbow) == tuple(), True)

        data = guide.get_hierarchy(wrist)
        self.assertEquals(data.get(wrist) == tuple(), True)

        wrist.set_parent(elbow)

        data = guide.get_hierarchy(elbow)

        self.assertEquals(data.get(elbow) == tuple(wrist), True)
        self.assertEquals(data.get(wrist) == tuple(), True)

    def test_duplicate(self):
        """[control.guide.duplicate]
        Generate new guide
        """

        elbow = guide.create("L", "elbow", index=0)

        new_elbow = guide.duplicate(elbow, hierarchy=False)[0]

        old_index = elbow.get_name().index
        new_index = new_elbow.get_name().index
        self.assertEquals((new_index - 1), old_index)

        # TODO:
        #   Test hierarchy duplication

    def test_set_parent(self):
        """[control.guide.set_parent]
        Set guide parent
        """

        elbow = guide.create("L", "elbow", index=0)
        wrist = guide.create("L", "wrist", index=0)

        guide.set_parent(wrist, elbow)

        self.assertEquals(wrist.get_parent(), elbow)

    def test_add_child(self):
        """[control.guide.add_child]
        Add child to guide
        """

        elbow = guide.create("L", "elbow", index=0)
        wrist = guide.create("L", "wrist", index=0)

        guide.add_child(elbow, wrist)

        self.assertEquals(elbow.get_child(wrist), wrist)

    def test_add_children(self):
        """[control.guide.add_children]
        Add children to guide
        """

        top = guide.create("C", "top", index=0)
        bottom_a = guide.create("C", "bottom", index=0)
        bottom_b = guide.create("C", "bottom", index=1)
        bottom_c = guide.create("C", "bottom", index=2)

        children = (bottom_a, bottom_b, bottom_c)
        guide.add_children(top, children)

        self.assertEquals(top.get_children(), children)

    def test_has_parent(self):
        """[control.guide.test_has_parent]
        Guide has parent
        """

        shoulder = guide.create("L", "shoulder", 0)
        elbow = guide.create("L", "elbow", 0)
        wrist = guide.create("L", "wrist", 0)

        wrist.set_parent(elbow)
        elbow.set_parent(shoulder)

        self.assertEquals(guide.has_parent(wrist, elbow), True)
        self.assertEquals(guide.has_parent(wrist, shoulder), True)
        self.assertEquals(guide.has_parent(elbow, shoulder), True)
        self.assertEquals(guide.has_parent(elbow, wrist), False)
        self.assertEquals(guide.has_parent(shoulder, elbow), False)
        self.assertEquals(guide.has_parent(shoulder, wrist), False)

    # def test_has_child(self):
    #     """[control.guide.None]
    #     """
    #     raise NotImplementedError

    # def test_is_parent(self):
    #     """[control.guide.None]
    #     """
    #     raise NotImplementedError

    def test_remove(self):
        """[control.guide.remove]
        Remove guide
        """

        elbow = guide.create("L", "elbow", 0)
        self.assertEquals(elbow.exists(), True)

        guide.remove(elbow)
        self.assertEquals(elbow.exists(), False)

    # def test_remove_parent(self):
    #     """[control.guide.None]
    #     """
    #     raise NotImplementedError

    def test_compile(self):
        """[control.guide.compile]
        Compile guides into joints
        """

        shoulder = guide.create("L", "shoulder", 0)
        elbow = guide.create("L", "elbow", 0)
        wrist = guide.create("L", "wrist", 0)

        wrist.set_parent(elbow)
        elbow.set_parent(shoulder)

        guide.compile()

        self.assertEquals(shoulder.exists(), False)
        self.assertEquals(elbow.exists(), False)
        self.assertEquals(wrist.exists(), False)

        # TODO:
        #   Make this more accurate
        joints = cmds.ls(type="joint")
        self.assertEquals(len(joints), 3)

    def test_get_guides(self):
        """[control.guide.get_guides]
        Get all guides in scene
        """

        shoulder = guide.create("L", "shoulder", 0)
        elbow = guide.create("L", "elbow", 0)
        wrist = guide.create("L", "wrist", 0)

        guides = sorted((shoulder, elbow, wrist))
        collect = sorted(guide.get_guides())

        self.assertEquals(guides, collect)

    def test_exists(self):
        """[control.guide.exists]
        Guide exists
        """

        arm = guide.create("L", "arm", 0)
        self.assertEquals(guide.exists(arm), True)

        arm.remove()
        self.assertEquals(guide.exists(arm), False)

    def test_set_aim_orient(self):
        """[control.guide.set_aim_orient]
        Set aim axis of input guide
        """

        arm = guide.create("L", "arm", 0)

        for order in Guide.ORIENT.keys():
            guide.set_aim_orient(arm, order)
            self.assertEquals(arm.get_aim_orient(), order)

        with self.assertRaises(Exception):
            arm.set_aim_orient("foo")

    def test_get_aim_orient(self):
        """[control.guide.get_aim_orient]
        Get aim orient of guide
        """

        arm = guide.create("L", "arm", 0)

        for order in Guide.ORIENT.keys():
            arm.set_aim_orient(order)
            self.assertEquals(guide.get_aim_orient(arm), order)

    def test_set_debug(self):
        """[control.guide.set_debug]
        Set guide debug
        """

        arm = guide.create("L", "arm", 0)

        guide.set_debug(arm, True)
        self.assertEquals(arm.is_debug(), True)

        guide.set_debug(arm, False)
        self.assertEquals(arm.is_debug(), False)

    def test_write(self):
        """[control.guide.write]
        Write snapshot to disk
        """

        arm = guide.create("L", "arm", 0)

        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        guide.write([arm], tmp.name)

        self.assertEquals(os.path.exists(tmp.name), True)
        os.remove(tmp.name)

    def test_read(self):
        """[control.guide.read]
        Read snapshot from disk
        """

        translates = (2, 4, 2)

        arm = guide.create("L", "arm", 0)
        arm.set_translates(*translates)

        snapshot = arm.get_snapshot()

        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        guide.write([arm], tmp.name)

        with self.assertRaises(Exception):
            guide.read("/path/does/not/exist.json")

        # Remove and create new guide
        guide.remove(arm)
        guide.create("L", "arm", 0)

        guide.restore(tmp.name)
        new_snapshot = arm.get_snapshot()
        self.assertEquals(new_snapshot, snapshot)

    def test_rebuild(self):
        """[control.guide.rebuild]
        Rebuild scene from data
        """

        translates = (2, 4, 2)

        arm = guide.create("L", "arm", 0)
        arm.set_translates(*translates)

        snapshot = arm.get_snapshot()

        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        guide.write([arm], tmp.name)

        with self.assertRaises(Exception):
            guide.read("/path/does/not/exist.json")

        # Remove and create new guide
        guide.remove(arm)
        cmds.file(new=True, force=True)

        guide.rebuild(tmp.name)
        arm_restore = guide.get_guides()[0]
        new_snapshot = arm_restore.get_snapshot()
        self.assertEquals(new_snapshot, snapshot)

    def test_validate(self):
        """[control.guide.validate]
        Validate dag node, confirm it's a guide
        """

        arm = guide.create("L", "arm", 12)
        self.assertIsInstance(guide.validate(arm), Guide)

        with self.assertRaises(Exception):
            guide.validate(None)

        with self.assertRaises(Exception):
            fake = cmds.createNode("joint", name="L_arm_0_gde")
            guide.validate(fake)
