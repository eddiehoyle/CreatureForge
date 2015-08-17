#!/usr/bin/env /Applications/Autodesk/maya2016/Maya.app/Contents/bin/mayapy

import unittest

from maya import cmds

from creatureforge.model.guide import Guide


class TestGuide(unittest.TestCase):

    def setUp(self):
        cmds.file(new=True, force=True)

    def tearDown(self):
        pass

    def test_create(self):
        """Create guide and check exists in Maya context"""

        g = Guide("L", "arm", 0)
        g.create()
        self.assertEquals(cmds.objExists(g.node), True)

    def test_name(self):
        """Test naming conventions and tokens"""

        g = Guide("L", "arm", 0)
        g.create()

        # Check tokens
        self.assertEquals(g.position, "L")
        self.assertEquals(g.description, "arm")
        self.assertEquals(g.index, 0)
        self.assertEquals(g.suffix, Guide.SUFFIX)
