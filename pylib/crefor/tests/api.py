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

    def __create(self):
        """
        """

        arm = api.create("L", "arm", 0)
        spine = api.create("C", "spine", 0)

        return arm, spine

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

        arm, _ = self.__create()
        self.assertEquals(api.exists(arm),
                          True,
                          "Guide does not exist: %s" % arm.node)

    def test_set_parent(self):
        """
        Test api.set_parent(child, parent)
        """

        child, parent = self.__create()

        api.set_parent(child, parent)

        self.assertEquals(child.parent.node,
                          parent.node,
                          "'%s' is not parent of '%s'" % (parent.node, child.node))
        self.assertEquals(child.node in [g.node for g in parent.children],
                          True,
                          "'%s' is not a child of '%s'" % (child.node, parent.node))

    def test_add_child(self):
        """
        Test api.add_child(parent, child)
        """

        child, parent = self.__create()

        api.add_child(parent, child)

        self.assertEquals(child.parent.node,
                          parent.node,
                          "'%s' is not parent of '%s'" % (parent.node, child.node))
        self.assertEquals(child.node in [g.node for g in parent.children],
                          True,
                          "'%s' is not a child of '%s'" % (child.node, parent.node))

    def test_has_parent(self):
        """
        Test api.has_parent(parent, child)
        """

        child, parent = self.__create()

        api.set_parent(child, parent)

        self.assertEquals(api.has_parent(child, parent),
                          True,
                          "'%s' is not parent of '%s'" % (parent.node, child.node))

    def test_has_child(self):
        """
        Test api.has_child(parent, child)
        """

        child, parent = self.__create()

        api.set_parent(child, parent)

        self.assertEquals(api.has_child(parent, child),
                          True,
                          "'%s' is not parent of '%s'" % (parent.node, child.node))

    def test_is_parent(self):
        """
        Test api.has_child(parent, child)
        """

        child, parent = self.__create()

        api.set_parent(child, parent)

        self.assertEquals(api.is_parent(parent, child),
                          True,
                          "'%s' is not parent of '%s'" % (parent.node, child.node))

    def test_remove(self):
        """
        Test api.remove(guide)
        """

        child, _ = self.__create()

        self.assertEquals(child.exists(),
                          True,
                          "Guide '%s' does not exist." % child.node)
        child.remove()

        self.assertEquals(child.exists(),
                          False,
                          "Guide '%s' does not exist." % child.node)

    def test_remove_parent(self):
        """
        Test api.remove_parent(guide)
        """

        child, parent = self.__create()

        api.set_parent(child, parent)

        api.remove_parent(child)

        self.assertEquals(api.is_parent(parent, child),
                          False,
                          "'%s' is not parent of '%s'" % (parent.node, child.node))

    def test_duplicate(self):
        """
        Test api.duplicate(guide)
        """

        child, _ = self.__create()

        self.assertEquals(api.exists(child),
                          True,
                          "Guide does not exist: %s" % child.node)

        duplicate = api.duplicate(child)

        self.assertEquals(child < duplicate and duplicate > child,
                          True,
                          "'%s' is not a duplicate of '%s'" % (duplicate, child))

    def test_compile(self):
        """
        Test api.compile()
        """

        child, _ = self.__create()

        self.assertEquals(api.exists(child),
                          True,
                          "Guide does not exist: '%s'" % child.node)

        api.compile()

        self.assertEquals(api.exists(child),
                          False,
                          "Guide exists: '%s'" % child.node)

        joint = libName.update(child.node, suffix="jnt")

        self.assertEquals(cmds.objExists(joint),
                          True,
                          "Joint does not exist: '%s'" % joint)

        guides = api.get_guides()
        self.assertEquals(guides == [],
                          True,
                          "Api listed guides after compiling: %s" % guides)

    def test_get_guides(self):
        """
        Test api.get_guides()
        """

        child, parent = self.__create()

        guides = api.get_guides()

        self.assertEquals(len(guides) == 2,
                          True,
                          "Failed to find all guides: '%s'" % guides)

        self.assertEquals(child in guides and parent in guides,
                          True,
                          "Created nodes are not listed: %s" % guides)

class TestApiReinit(TestApi):

    def __create(self):
        """
        """

        arm = api.create("L", "arm", 0)
        spine = api.create("C", "spine", 0)

        arm = arm.reinit()
        spine = spine.reinit()

        return arm, spine