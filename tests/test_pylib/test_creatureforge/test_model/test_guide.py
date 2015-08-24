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

# ------------------------------------------------------------------------------

def create_arm():
    guide = Guide(POSITION, DESCRIPTION, index=INDEX)
    guide.create()
    return guide

def create_wrist():
    guide = Guide(POSITION, "wrist", index=INDEX)
    guide.create()
    return guide

# ------------------------------------------------------------------------------

# class TestModelGuide(unittest.TestCase):

#     def setUp(self):
#         cmds.file(new=True, force=True)

#     def tearDown(self):
#         pass

#     def test_create(self):
#         """[model.guide.Guide.create]
#         Create guide and check exists in Maya context
#         """

#         arm = Guide(POSITION, DESCRIPTION, index=INDEX)

#         with self.assertRaises(Exception):
#             arm.get_node()

#         self.assertEquals(arm.exists(), False)

#         arm.create()
#         node = arm.get_node()
#         self.assertEquals(cmds.objExists(node), True)

#         self.assertEquals(arm.exists(), True)

#     def test_get_aim(self):
#         """[model.guide.Guide.get_aim]
#         Aim transform exists
#         """

#         arm = Guide(POSITION, DESCRIPTION, index=INDEX)

#         with self.assertRaises(Exception):
#             arm.get_aim()

#         arm.create()
#         aim = arm.get_aim()
#         self.assertEquals(cmds.objExists(aim), True)

#     def test_get_up(self):
#         """[model.guide.Guide.get_up]
#         Up node exists
#         """

#         arm = Guide(POSITION, DESCRIPTION, index=INDEX)

#         with self.assertRaises(Exception):
#             arm.get_up()

#         arm.create()
#         up = arm.get_up()
#         self.assertEquals(cmds.objExists(up.get_node()), True)

#     def test_get_setup(self):
#         """[model.guide.Guide.get_setup]
#         Setup transform exists
#         """

#         arm = Guide(POSITION, DESCRIPTION, index=INDEX)

#         with self.assertRaises(Exception):
#             arm.get_setup()

#         arm.create()
#         setup = arm.get_setup()
#         self.assertEquals(cmds.objExists(setup), True)

#     def test_get_shapes(self):
#         """[model.guide.Guide.get_shapes]
#         Shapes exists under guide
#         """

#         arm = Guide(POSITION, DESCRIPTION, index=INDEX)

#         with self.assertRaises(Exception):
#             arm.get_shapes()

#         arm.create()
#         shapes = arm.get_shapes()
#         for shape in shapes:
#             self.assertEquals(cmds.objExists(shape), True)

#     def test_get_constraint(self):
#         """[model.guide.Guide.get_constraint]
#         Aim constraint node exists
#         """

#         arm = Guide(POSITION, DESCRIPTION, index=INDEX)

#         with self.assertRaises(Exception):
#             arm.get_constraint()

#         arm.create()
#         constraint = arm.get_constraint()
#         self.assertEquals(cmds.objExists(constraint), True)

#     def test_get_condition(self):
#         """[model.guide.Guide.get_condition]
#         Aim condition node exists
#         """

#         arm = Guide(POSITION, DESCRIPTION, index=INDEX)

#         with self.assertRaises(Exception):
#             arm.get_condition()

#         arm.create()
#         condition = arm.get_condition()
#         self.assertEquals(cmds.objExists(condition), True)

#     def test_get_parent(self):
#         """[model.guide.Guide.get_parent]
#         Get Guide parent
#         """

#         arm = Guide(POSITION, DESCRIPTION, index=INDEX)

#         with self.assertRaises(Exception):
#             arm.get_parent()

#         arm.create()
#         parent = arm.get_parent()
#         self.assertIsNone(parent)

#     def test_get_children(self):
#         """[model.guide.Guide.get_children]
#         Guide has children
#         """

#         arm = Guide(POSITION, DESCRIPTION, index=INDEX)

#         with self.assertRaises(Exception):
#             arm.get_children()

#         arm.create()
#         children = arm.get_children()
#         self.assertIsInstance(children, tuple)
#         self.assertEquals(len(children), 0)

#     def test_get_aim_at(self):
#         """[model.guide.Guide.get_aim_at]
#         Get which guide parent guide is aiming at
#         """

#         arm = Guide(POSITION, DESCRIPTION, index=INDEX)

#         with self.assertRaises(Exception):
#             arm.get_aim_at()

#         arm.create()

#         aim_at = arm.get_aim_at()
#         self.assertIsNone(aim_at)

#     def test_get_aim_orient(self):
#         """[model.guide.Guide.get_aim_orient]
#         Get guide aim orient
#         """

#         arm = Guide(POSITION, DESCRIPTION, index=INDEX)

#         with self.assertRaises(Exception):
#             arm.get_aim_orient()

#         arm.create()

#         aim_orient = arm.get_aim_orient()
#         self.assertIsInstance(aim_orient, tuple)
#         self.assertEquals(len(aim_orient), 3)

#     def test_get_offset_orient(self):
#         """[model.guide.Guide.get_offset_orient]
#         Get guide offset orient """

#         arm = Guide(POSITION, DESCRIPTION, index=INDEX)

#         with self.assertRaises(Exception):
#             arm.get_offset_orient()

#         arm.create()

#         offset_orient = arm.get_offset_orient()
#         self.assertIsInstance(offset_orient, tuple)
#         self.assertEquals(len(offset_orient), 3)

#     def test_get_translates(self):
#         """[model.guide.Guide.get_translates]
#         Get translates
#         """

#         arm = Guide(POSITION, DESCRIPTION, index=INDEX)

#         with self.assertRaises(Exception):
#             arm.get_translates()

#         arm.create()
#         self.assertEquals(arm.get_translates(), (0, 0, 0))

#         translates = (0, 3, 0)
#         arm.set_translates(*translates)
#         self.assertEquals(arm.get_translates(), translates)

#     def test_set_translates(self):
#         """[model.guide.Guide.set_translates]
#         """

#         arm = Guide(POSITION, DESCRIPTION, index=INDEX)
#         arm.create()

#         translates = (0, 3, 0)
#         arm.set_translates(*translates)
#         self.assertEquals(arm.get_translates(), translates)

#     def test_copy(self):
#         """[model.guide.Guide.copy]
#         """

#         arm = Guide(POSITION, DESCRIPTION, index=INDEX)
#         arm.create()

#         new = arm.copy()

#         index = new.get_name().index
#         self.assertEquals(index - 1, INDEX)

#     def test_remove(self):
#         """[model.guide.Guide.remove]
#         """

#         arm = Guide(POSITION, DESCRIPTION, index=INDEX)

#         with self.assertRaises(Exception):
#             arm.remove()

#         arm.create()

#         dag = arm.get_dag()
#         nondag = arm.get_nondag()
#         arm.remove()

#         for data in [dag, nondag]:
#             for key, value in dag.iteritems():
#                 if not isinstance(value, (tuple, list, set)):
#                     value = [value]
#                 for node in value:
#                     self.assertEquals(cmds.objExists(node), False)

#     def test_get_snapshot(self):
#         """[model.guide.Guide.get_snapshot]
#         Guide snapshot is created with correct data
#         """

#         arm = Guide(POSITION, DESCRIPTION, index=INDEX)

#         with self.assertRaises(Exception):
#             arm.get_snapshot()

#         arm.create()

#         snapshot = arm.get_snapshot()

#         self.assertEquals(snapshot["node"], arm.get_node())
#         self.assertEquals(snapshot["parent"], arm.get_parent())
#         self.assertEquals(snapshot["children"], arm.get_children())
#         self.assertEquals(snapshot["aim_orient"], arm.get_aim_orient())
#         self.assertEquals(snapshot["offset_orient"], arm.get_offset_orient())
#         self.assertEquals(snapshot["aim_at"], arm.get_aim_at())
#         self.assertEquals(snapshot["aim_flip"], arm.get_aim_flip())
#         self.assertEquals(snapshot["translates"], arm.get_translates())
#         self.assertEquals(snapshot["up_translates"], arm.get_up().get_translates())

#     def test_compile(self):
#         """[model.guide.Guide.compile]
#         Guide compiles to joint
#         """

#         arm = Guide(POSITION, DESCRIPTION, index=INDEX)

#         with self.assertRaises(Exception):
#             arm.compile()

#         arm.create()
#         joint = arm.compile()
#         self.assertEquals(cmds.objExists(joint), True)


class TestModelGuideHierarchy(unittest.TestCase):

    def setUp(self):
        cmds.file(new=True, force=True)

    def tearDown(self):
        pass

    def test_get_parent(self):
        """[model.guide.Guide.get_parent]
        Guide returns parent correctly
        """

        arm = create_arm()
        wrist = create_wrist()

        wrist.set_parent(arm)

        self.assertEquals(wrist.get_parent(), arm)

    # def test_get_children(self):
    #     """[model.guide.Guide.None]
    #     """
    #     raise NotImplementedError

    # def test_get_aim_at(self):
    #     """[model.guide.Guide.None]
    #     """
    #     raise NotImplementedError

    # def test_has_parent(self):
    #     """[model.guide.Guide.None]
    #     """
    #     raise NotImplementedError

    # def test_has_child(self):
    #     """[model.guide.Guide.None]
    #     """
    #     raise NotImplementedError

    # def test_set_parent(self):
    #     """[model.guide.Guide.None]
    #     """
    #     raise NotImplementedError

    # def test_add_child(self):
    #     """[model.guide.Guide.None]
    #     """
    #     raise NotImplementedError

    # def test_remove_parent(self):
    #     """[model.guide.Guide.None]
    #     """
    #     raise NotImplementedError

    # def test_remove_child(self):
    #     """[model.guide.Guide.None]
    #     """
    #     raise NotImplementedError
    
    # def test_remove(self):
    #     """[model.guide.Guide.remove]
    #     Set hierarchy and remove guides
    #     """
    #     raise NotImplementedError