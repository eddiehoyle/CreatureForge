#!/usr/bin/env /Applications/Autodesk/maya2016/Maya.app/Contents/bin/mayapy

import unittest

from maya import cmds

from creatureforge.control import guide
from creatureforge.model.guide import Guide
from creatureforge.model.guide import Up

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
