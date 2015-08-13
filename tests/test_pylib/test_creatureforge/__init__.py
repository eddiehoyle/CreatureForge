#!/usr/bin/env /Applications/Autodesk/maya2016/Maya.app/Contents/bin/mayapy

import unittest

from maya import cmds

from creatureforge.model.guide import Guide


class TestGuide(unittest.TestCase):

    def test_create(self):
        """
        Create guide
        """

        g = Guide("L", "arm", 0)
        g.create()
        self.assertEquals(cmds.objExists(g.node), True)
