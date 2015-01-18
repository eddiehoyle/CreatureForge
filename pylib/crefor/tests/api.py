#!/usr/bin/env python

"""
"""

from maya import cmds
from crefor import api
from crefor.lib import libName
from crefor import log

import unittest
import logging

logger = log.get_logger(__name__)
logger.setLevel(logging.CRITICAL)
logger.disabled = True

class TestApi(unittest.TestCase):

    def setUp(self):
        """Runs before each test"""
        cmds.file(newFile=True, force=True)

    def tearDown(self):
        """Runs after each test"""
        pass

    def test_create(self):
        """
        Test api.create()
        """

        guide = api.create("L", "arm", 0).create()
        self.assertEquals(api.exists(guide),
                          True,
                          "Guide does not exist: %s" % guide.name)

    def test_set_parent(self):
        """
        Test api.set_parent(child, parent)
        """

        parent = api.create("L", "arm", 0).create()
        child = api.create("L", "arm", 1).create()

        api.set_parent(child, parent)

        self.assertEquals(child.parent.joint,
                          parent.joint,
                          "'%s' is not parent of '%s'" % (parent.joint, child.joint))
        self.assertEquals(child.joint in [g.name for g in parent.children],
                          True,
                          "'%s' is not a child of '%s'" % (child.joint, parent.joint))

    def test_add_child(self):
        """
        Test api.add_child(parent, child)
        """

        parent = api.create("L", "arm", 0).create()
        child = api.create("L", "arm", 1).create()

        api.add_child(parent, child)

        self.assertEquals(child.parent.joint,
                          parent.joint,
                          "'%s' is not parent of '%s'" % (parent.joint, child.joint))
        self.assertEquals(child.joint in [g.name for g in parent.children],
                          True,
                          "'%s' is not a child of '%s'" % (child.joint, parent.joint))

    def test_has_parent(self):
        """
        Test api.has_parent(parent, child)
        """

        parent = api.create("L", "arm", 0).create()
        child = api.create("L", "arm", 1).create()

        api.set_parent(child, parent)

        self.assertEquals(api.has_parent(child, parent),
                          True,
                          "'%s' is not parent of '%s'" % (parent.joint, child.joint))

    def test_has_child(self):
        """
        Test api.has_child(parent, child)
        """

        parent = api.create("L", "arm", 0).create()
        child = api.create("L", "arm", 1).create()

        api.set_parent(child, parent)

        self.assertEquals(api.has_child(parent, child),
                          True,
                          "'%s' is not parent of '%s'" % (parent.joint, child.joint))

    def test_is_parent(self):
        """
        Test api.has_child(parent, child)
        """

        parent = api.create("L", "arm", 0).create()
        child = api.create("L", "arm", 1).create()

        api.set_parent(child, parent)

        self.assertEquals(api.is_parent(parent, child),
                          True,
                          "'%s' is not parent of '%s'" % (parent.joint, child.joint))

    def test_remove(self):
        """
        Test api.remove(guide)
        """

        guide = api.create("L", "arm", 0).create()

        self.assertEquals(guide.exists(),
                          True,
                          "Guide '%s' does not exist." % guide.joint)
        guide.remove()

        self.assertEquals(guide.exists(),
                          False,
                          "Guide '%s' does not exist." % guide.joint)

    def test_remove_parent(self):
        """
        Test api.remove_parent(guide)
        """

        parent = api.create("L", "arm", 0).create()
        child = api.create("L", "arm", 1).create()

        api.set_parent(child, parent)

        self.assertEquals(api.is_parent(parent, child),
                          True,
                          "'%s' is not parent of '%s'" % (parent.joint, child.joint))

        api.remove_parent(child)

        self.assertEquals(api.is_parent(parent, child),
                          False,
                          "'%s' is not parent of '%s'" % (parent.joint, child.joint))

    def test_duplicate(self):
        """
        Test api.duplicate(guide)
        """

        guide = api.create("L", "arm", 0).create()
        self.assertEquals(api.exists(guide),
                          True,
                          "Guide does not exist: %s" % guide.name)

        duplicate = api.duplicate(guide)
        self.assertEquals(guide < duplicate and duplicate > guide,
                          True,
                          "'%s' is not a duplicate of '%s'" % (duplicate, guide))

    def test_reinit(self):
        """
        Test api.reinit(guide)
        """

        from crefor.model.guide.guide import Guide

        guide = api.create("L", "arm", 0).create()

        reinit_guide = api.reinit(guide.name)
        self.assertEquals(isinstance(reinit_guide, Guide),
                          True,
                          "Failed to reinit guide: '%s'" % reinit_guide)

    def test_compile(self):
        """
        Test api.compile()
        """

        guide = api.create("L", "arm", 0).create()
        self.assertEquals(api.exists(guide),
                          True,
                          "Guide does not exist: '%s'" % guide.name)

        api.compile()
        self.assertEquals(api.exists(guide),
                          False,
                          "Guide exists: '%s'" % guide.name)

        joint = libName.update(guide.name, suffix="jnt")
        self.assertEquals(cmds.objExists(joint),
                          True,
                          "Joint does not exist: '%s'" % joint)

    def test_get_guides(self):
        """
        Test api.get_guides()
        """

        api.create("L", "arm", 0).create()
        api.create("L", "arm", 1).create()

        guides = api.get_guides()

        self.assertEquals(len(guides) == 2,
                          True,
                          "Failed to find all guides: '%s'" % guides)

    def test_set_axis(self):
        """
        Test set_axis(guide, axis)
        """

        guide = api.create("L", "arm", 0).create()

        from crefor.model.guide.guide import Guide

        for axis in Guide.AIM_ORDER.keys():
            api.set_axis(guide, primary=axis[0], secondary=axis[1])
            self.assertEquals(guide.get_axis(),
                              axis,
                              "Queried guide axis. Expected '%s', got '%s'" % (axis, guide.get_axis()))

    def test_write(self):
        """
        """

        pass

    def test_read(self):
        """
        """

        pass
