#!/usr/bin/env /Applications/Autodesk/maya2016/Maya.app/Contents/bin/mayapy

import os
import tempfile
import unittest
from pprint import pprint

from maya import cmds

from creatureforge.model.gen import name

# ------------------------------------------------------------------------------

POSITION = "L"
PRIMARY = "arm"
PRIMARY_INDEX = 0
SECONDARY = "fk"
SECONDARY_INDEX = 0
SUFFIX = "ctl"

# ------------------------------------------------------------------------------

class TestNameModel(unittest.TestCase):

    def setUp(self):
        cmds.file(new=True, force=True)

    def tearDown(self):
        pass

    def test_create(self):
        """[model.gen.name.NameModel]
        """

        example = "L_arm_0_fk_0_ctl"

        n = name.NameModel(POSITION,
                           PRIMARY,
                           PRIMARY_INDEX,
                           SECONDARY,
                           SECONDARY_INDEX,
                           SUFFIX)
        compiled = n.compile()

        self.assertEquals(compiled, example)

    def test_position(self):
        """[model.gen.name.NameModel.position]
        """

        n = name.NameModel(POSITION,
                           PRIMARY,
                           PRIMARY_INDEX,
                           SECONDARY,
                           SECONDARY_INDEX,
                           SUFFIX)

        self.assertEquals(n.position, POSITION)

        for invalid in ["1", 1, "_"]:
            with self.assertRaises(Exception):
                n = name.NameModel(invalid,
                                   PRIMARY,
                                   PRIMARY_INDEX,
                                   SECONDARY,
                                   SECONDARY_INDEX,
                                   SUFFIX)

    def test_primary(self):
        """[model.gen.name.NameModel.primary]
        """

        n = name.NameModel(POSITION,
                           PRIMARY,
                           PRIMARY_INDEX,
                           SECONDARY,
                           SECONDARY_INDEX,
                           SUFFIX)

        self.assertEquals(n.primary, PRIMARY)

        for invalid in ["1", 1, "_", "2arm", "_arm", "_1"]:
            with self.assertRaises(Exception):
                n = name.NameModel(POSITION,
                                   invalid,
                                   PRIMARY_INDEX,
                                   SECONDARY,
                                   SECONDARY_INDEX,
                                   SUFFIX)

    def test_primary_index(self):
        """[model.gen.name.NameModel.primary_index]
        """

        n = name.NameModel(POSITION,
                           PRIMARY,
                           PRIMARY_INDEX,
                           SECONDARY,
                           SECONDARY_INDEX,
                           SUFFIX)

        self.assertEquals(n.primary_index, PRIMARY_INDEX)

        for invalid in ["_", "a", "_5"]:
            with self.assertRaises(Exception):
                n = name.NameModel(POSITION,
                                   PRIMARY,
                                   invalid,
                                   SECONDARY,
                                   SECONDARY_INDEX,
                                   SUFFIX)

    def test_secondary(self):
        """[model.gen.name.NameModel.secondary]
        """

        n = name.NameModel(POSITION,
                           PRIMARY,
                           PRIMARY_INDEX,
                           SECONDARY,
                           SECONDARY_INDEX,
                           SUFFIX)

        self.assertEquals(n.secondary, SECONDARY)

        for invalid in ["1", 1, "_", "2arm", "_arm", "_1"]:
            with self.assertRaises(Exception):
                n = name.NameModel(POSITION,
                                   PRIMARY,
                                   PRIMARY_INDEX,
                                   invalid,
                                   SECONDARY_INDEX,
                                   SUFFIX)

    def test_secondary_index(self):
        """[model.gen.name.NameModel.secondary_index]
        """

        n = name.NameModel(POSITION,
                           PRIMARY,
                           PRIMARY_INDEX,
                           SECONDARY,
                           SECONDARY_INDEX,
                           SUFFIX)

        self.assertEquals(n.secondary_index, SECONDARY_INDEX)

        for invalid in ["_", "a", "_5"]:
            with self.assertRaises(Exception):
                n = name.NameModel(POSITION,
                                   PRIMARY,
                                   PRIMARY_INDEX,
                                   SECONDARY,
                                   invalid,
                                   SUFFIX)

    def test_suffix(self):
        """[model.gen.name.NameModel.suffix]
        """

        n = name.NameModel(POSITION,
                           PRIMARY,
                           PRIMARY_INDEX,
                           SECONDARY,
                           SECONDARY_INDEX,
                           SUFFIX)

        self.assertEquals(n.suffix, SUFFIX)

        for invalid in ["1", 1, "_", "2arm", "_arm", "_1"]:
            with self.assertRaises(Exception):
                n = name.NameModel(POSITION,
                                   PRIMARY,
                                   PRIMARY_INDEX,
                                   SECONDARY,
                                   SUFFIX,
                                   invalid)

    def test_rename(self):
        """[model.gen.name.NameModel.rename]
        """

        n = name.NameModel(POSITION,
                           PRIMARY,
                           PRIMARY_INDEX,
                           SECONDARY,
                           SECONDARY_INDEX,
                           SUFFIX)

        new_position = "C"
        new_primary = "spine"
        new_primary_index = 2
        new_secondary = "ik"
        new_secondary_index = 2
        new_suffix = "grp"

        n.rename(position=new_position)
        self.assertEquals(n., )
