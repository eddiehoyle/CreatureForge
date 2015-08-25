#!/usr/bin/env /Applications/Autodesk/maya2016/Maya.app/Contents/bin/mayapy

import unittest

from maya import cmds

from creatureforge.control import guide
from creatureforge.model.guide import Guide
from creatureforge.model.up import Up

# ------------------------------------------------------------------------------

POSITION = "L"
DESCRIPTION = "arm"
INDEX = 0

# ------------------------------------------------------------------------------


class TestModelUp(unittest.TestCase):

    def setUp(self):
        cmds.file(new=True, force=True)

    def tearDown(self):
        pass

    def test_create(self):
        """[model.up.Up.create]
        Create guide and check exists in Maya context
        """

        arm = Guide(POSITION, DESCRIPTION, index=INDEX)

        with self.assertRaises(Exception):
            arm.get_up()

        arm.create()

        up = arm.get_up()
        self.assertIsInstance(up, Up)
        self.assertEquals(cmds.objExists(up.get_node()), True)

    def test_get_translates(self):
        """[model.up.Up.get_translates]
        Get translates of Up node
        """

        arm = Guide(POSITION, DESCRIPTION, index=INDEX)
        arm.create()
        up = arm.get_up()

        translates = up.get_translates()
        self.assertEquals(translates, (0, 3, 0))

    def test_set_translates(self):
        """[model.up.Up.set_translates]
        Get translates of Up node
        """

        arm = Guide(POSITION, DESCRIPTION, index=INDEX)
        arm.create()
        up = arm.get_up()

        translates = (1, 2, 3)

        up.set_translates(*translates)
        self.assertEquals(up.get_translates(), translates)

        # TODO:
        #   Test local/worldspace

    def test_get_guide(self):
        """[model.up.Up.get_guide]
        Get source guide of Up node
        """

        arm = Guide(POSITION, DESCRIPTION, index=INDEX)
        arm.create()
        up = arm.get_up()

        self.assertEquals(up.get_guide(), arm)

    def test_get_group(self):
        """[model.up.Up.None]
        Get up group transform
        """

        arm = Guide(POSITION, DESCRIPTION, index=INDEX)
        arm.create()
        up = arm.get_up()

        group = up.get_group()
        self.assertEquals(cmds.objExists(group), True)
        self.assertEquals(cmds.nodeType(group), "transform")

    def test_get_shapes(self):
        """[model.up.Up.None]
        Get up shapes
        """

