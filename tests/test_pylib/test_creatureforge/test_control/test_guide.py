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
        """[control.guide] Create guide and check exists in Maya context"""

        g = guide.create("L", "arm", index=0)
        self.assertEquals(cmds.objExists(g.node), True)
        self.assertIsInstance(g, Guide)
