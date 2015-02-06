#!/usr/bin/env python

"""
"""

from maya import cmds
from crefor.model.guide import Guide
from crefor.lib import libName

import unittest

class TestGuide(unittest.TestCase):

    def __create(self):
        """
        """

        arm = Guide("L", "arm", 0)
        arm.create()

        spine = Guide("C", "spine", 0)
        spine.create()

        return arm, spine

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

        arm, _ = self.__create()

        self.assertEquals(cmds.objExists(arm.node),
                          True,
                          "Guide does not exist: %s" % arm.node)

        for key, nodes in arm.nodes.items():
            if not isinstance(nodes, list):
                nodes = [nodes]
            for node in nodes:
                self.assertEquals(cmds.objExists(node),
                                  True,
                                  "Node does not exist: %s" % node)

    def test_reinit(self):
        """
        Test reinit()
        """

        arm, _ = self.__create()

        arm = Guide(*libName.decompile(str(arm), 3)).reinit()

        self.assertEquals(cmds.objExists(arm.node),
                          True,
                          "Guide does not exist: %s" % arm.node)

        for key, nodes in arm.nodes.items():
            if not isinstance(nodes, list):
                nodes = [nodes]
            for node in nodes:
                self.assertEquals(cmds.objExists(node),
                                  True,
                                  "Node does not exist: %s" % node)

        spine = Guide("C", "spine", 0)
        self.assertRaises(Exception,
                          spine.reinit,
                          [],
                          "Guide reinit did not raise exception: %s" % spine)

    def test_validate(self):
        """
        Test validate()
        """

        arm, _ = self.__create()
        obj = Guide.validate(arm.node)

        self.assertEquals(isinstance(obj, Guide),
                          True,
                          "Validate did not return a Guide object: %s" % arm)

        self.assertRaises(Exception,
                          Guide.validate,
                          ["C_spine_0_gde"],
                          "Validated failed to raise exception invalid args")

    def test_nodes(self):
        """
        Test nodes property
        """

        arm, _ = self.__create()

        for key in arm.nodes:
            self.assertEquals(hasattr(arm, key), True, "Guide object is missing attribute: '%s'" % key)

    def test_setup(self):
        """
        Test setup
        """


        arm, _ = self.__create()

        self.assertEquals(cmds.objExists(arm.setup), True, "Setup node does not exist: '%s'" % arm.setup)

    def test_short_name(self):
        """
        Test short_name property
        """

        arm, _ = self.__create()

        self.assertEquals(arm.short_name, arm.node, "Short name '%s' does not match joint: '%s'" % (arm.short_name, arm.node))

    def test_long_name(self):
        """
        Test long_name property
        """

        arm, _ = self.__create()

        p1 = cmds.createNode("transform", name=arm.setup)
        cmds.createNode("joint", name=arm.node, parent=p1)

        p2 = cmds.createNode("transform", name=arm.setup)
        cmds.createNode("joint", name=arm.node, parent=p2)

        p3 = cmds.createNode("transform", name=arm.setup)
        cmds.createNode("joint", name=arm.node, parent=p3)

        self.assertEquals(isinstance(Guide("L", "arm", 0).reinit(), Guide),
                          True,
                          "Guide did not reinit with duplicate names correctly: '%s'" % arm.long_name)

    def test_parent(self):
        """
        Test parent property
        """

        arm, spine = self.__create()

        self.assertIsNone(arm.parent, "Guide did not return None as parent: '%s'" % arm.node)

        arm.set_parent(spine)

        self.assertEquals(arm.parent.node, spine.node, "Guide's parent do not match: '%s' --> '%s'" % (arm.node, spine.node))

    def test_children(self):
        """
        Test children property
        """

        arm, spine = self.__create()

        self.assertEquals(arm.children, [], "Guide did not return [] as children: '%s'" % arm.node)

        spine.add_child(arm)

        self.assertEquals(arm in spine.children, True, "Guide '%s' is not a child of '%s'" % (arm.node, spine.node))

    def test_connectors(self):
        """
        Test connectors are linked to children
        """

        arm, _ = self.__create()

        for i in range(3):
            wrist = Guide("L", "wrist", i)
            wrist.create()

            arm.add_child(wrist)

        for con, child in zip(arm.connectors, arm.children):
            self.assertEquals(con.parent, arm, "Connector parent is not parent guide: '%s'" % arm)
            self.assertEquals(con.child, child, "Connector parent is not parent guide: '%s'" % arm)

    def test_exists(self):
        """
        Test guide exists before and after remove
        """

        arm, _ = self.__create()

        self.assertEquals(arm.exists(), True, "Guide does not exist: '%s'" % arm.node)

        arm.remove()

        self.assertEquals(arm.exists(), False, "Guide does not exist: '%s'" % arm.node)

    def test_strip(self):
        """
        Test strip() guide
        """

        arm, spine = self.__create()

        spine.set_parent(arm)

        arm.strip()

        self.assertIsNone(spine.parent, "Guide did not return None as parent: '%s'" % spine.node)
        self.assertEquals(arm.children, [], "Guide did not return empty list as children: '%s'" % arm.children)

    # def test_scale(self):
    #     """
    #     Test set_scale on joints
    #     """

    #     arm, _ = self.__create()

    #     arm.set_scale(2)

    #     # Scale only affects shapes
    #     self.assertEquals(cmds.getAttr("%s.scale" % arm.node)[0], (1.0, 1.0, 1.0), "Guide scale is not [1, 1, 1]: '%s'" % arm.node)

    def get_translates(self):
        """
        Test get_translates
        """

        arm, _ = self.__create()

        move_pos = [0, 4, 0]
        arm.set_position(move_pos)

        self.assertEquals(arm.get_translates(), move_pos)

    def test_set_axis(self):
        """
        Test set_axis()
        """

        arm, _ = self.__create()

        for axis in Guide.AIM_ORIENT.keys():
            arm.set_axis(*axis[:2])

    def test_primary(self):
        """
        Test primary property
        """

        arm = Guide("L", "arm", 0)
        arm.create()

        for axis in Guide.AIM_ORIENT:
            arm.set_axis(*axis[:2])
            self.assertEquals(arm.primary, axis[0], "Primary axis '%s' does not match: '%s'" % (arm.primary, axis[0]))

    def test_secondary(self):
        """
        Test secondary property
        """

        arm, _ = self.__create()

        for axis in Guide.AIM_ORIENT:
            arm.set_axis(*axis[:2])
            self.assertEquals(arm.secondary, axis[1], "Secondary axis '%s' does not match: '%s'" % (arm.secondary, axis[1]))

    def test_aim_at(self):
        """
        Test aim_at()
        """

        arm, spine = self.__create()

        self.assertRaises(Exception,
                          arm.aim_at,
                          [spine],
                          "Tried to aim at a guide that wasn't a child, no exception was raised.")

        arm.aim_at(spine, add=True)
        self.assertEquals(spine.parent, arm, "Guide's parent do not match: '%s' --> '%s'" % (arm, spine))
        self.assertEquals(spine in arm.children, True, "Guide '%s' is not a child of '%s'" % (spine, arm))

        enums = cmds.attributeQuery('aimAt', node=arm.node, listEnum=True)[0].split(':')

        self.assertEquals(spine.node in enums, True, "Guide aim is not in aim_at enums: '%s', %s" % (spine.node, enums))


class TestGuideReinit(TestGuide):
    """
    Repeat all tests but after being reinitialised from string
    """

    def __create(self):
        arm = Guide("L", "arm", 0)
        arm.create()

        spine = Guide("C", "spine", 0)
        spine.create()

        arm = Guide(*libName.decompile(arm.node, 3)).reinit()
        spine = Guide(*libName.decompile(spine.node, 3)).reinit()

        return arm, spine
