#!/usr/bin/env /Applications/Autodesk/maya2016/Maya.app/Contents/bin/mayapy

import unittest

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

    # def test_exists(self):
    #     """[control.guide.None]
    #     """
    #     raise NotImplementedError

    # def test_set_axis(self):
    #     """[control.guide.None]
    #     """
    #     raise NotImplementedError

    # def test_set_debug(self):
    #     """[control.guide.None]
    #     """
    #     raise NotImplementedError

    # def test_write(self):
    #     """[control.guide.None]
    #     """
    #     raise NotImplementedError

    # def test_read(self):
    #     """[control.guide.None]
    #     """
    #     raise NotImplementedError

    # def test_rebuild(self):
    #     """[control.guide.None]
    #     """
    #     raise NotImplementedError

    # def test_validate(self):
    #     """[control.guide.None]
    #     """
    #     raise NotImplementedError

