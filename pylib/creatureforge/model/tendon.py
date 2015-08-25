#!/usr/bin/env python

"""
"""

import time
import logging
from collections import OrderedDict

from maya import cmds

from creatureforge.lib import libname
from creatureforge.lib import libattr
from creatureforge.lib import libutil
from creatureforge.lib import libconstraint
from creatureforge.decorators import Memoized
from creatureforge.model.base import Module
from creatureforge.exceptions import DuplicateNameError
from creatureforge.exceptions import GuideDoesNotExistError
from creatureforge.exceptions import GuideHierarchyError


class GuideError(Exception):
    pass

logger = logging.getLogger(__name__)

AXIS = ["X", "Y", "Z"]


def cache(func):
    def wraps(*args, **kwargs):
        node = args[0].node
        if not cmds.objExists(node):
            err = "Guide does not exist: '{node}'".format(node=node)
            raise RuntimeError(err)
        return func(*args, **kwargs)
    return wraps


class Tendon(Module):

    SUFFIX = "cncShape"

    def __init__(self, child, parent):

        self.__child = child
        self.__parent = parent

        super(Tendon, self).__init__(*child.tokens)

    @cache
    def get_condition(self):
        return self._nondag.get("condition")

    @cache
    def get_child(self):
        return self.__child

    @cache
    def get_parent(self):
        return self.__parent

    def __create_annotation(self):
        shape = cmds.createNode("annotationShape", name=self.get_name())
        transform = cmds.listRelatives(shape, parent=True)[0]

        parent = self.get_parent()
        cmds.parent(self.get_node(), parent.node, shape=True, relative=True)
        cmds.delete(transform)

        libattr.set(self.get_node(), "overrideEnabled", True)
        libattr.set(self.get_node(), "overrideColor", 18)
        libattr.set(self.get_node(), "displayArrow", False)
        libattr.set(self.get_node(), "displayArrow", True)
        cmds.connectAttr("{src}.worldMatrix[0]".format(src=self.get_child().get_shapes()[0]),
                         "{dst}.dagObjectMatrix[0]".format(dst=self.get_node()),
                         force=True)

    def __create_aim(self):

        parent = self.get_parent()
        child = self.get_child()

        # Query aliases and target list from parent aim constraint
        aim_handler = libconstraint.get_handler(parent.get_constraint())
        aliases = aim_handler.aliases
        targets = aim_handler.targets
        index = targets.index(self.get_child().get_aim())

        # Query parent joint enum items
        enums = cmds.attributeQuery("guideAimAt", node=parent.get_node(), listEnum=True)[0].split(":")
        enum_index = enums.index(child.get_node())

        # Create condition that turns on aim for child constraint if
        # enum index is set to match childs name
        condition = cmds.createNode(
            "condition",
            name=libname.rename(
                self.get_node(),
                append=self.description,
                suffix="cond"))

        libattr.set(condition, "secondTerm", enum_index)
        libattr.set(condition, "colorIfTrueR", 1)
        libattr.set(condition, "colorIfFalseR", 0)

        cmds.connectAttr("%s.guideAimAt" % parent.node, "%s.firstTerm" % condition)
        cmds.connectAttr("%s.outColorR" % condition, "%s.%s" % (parent.get_constraint(), aliases[index]))

        # Set enum to match child aim
        libattr.set(parent.node, "guideAimAt", enum_index)

        # Loop through all aliases on and set non-connected attributes to be 0
        for alias in aliases:
            if not cmds.listConnections('%s.%s' % (parent.get_constraint(), alias),
                                        source=True,
                                        destination=False,
                                        plugs=True):
                libattr.set(parent.get_constraint(), alias, 0)

        # Store new condition
        self.store("condition", condition, dag=False)

    def __update_aim_index(self):
        if self.exists:

            # Query parent joint enum items
            enums = cmds.attributeQuery("guideAimAt", node=self.__parent.node, listEnum=True)[0].split(':')
            enum_index = enums.index(self.__child.node)

            # Update index to reflect alias index of child
            parent = self.get_parent()
            libattr.set(parent.get_condition(), "secondTerm", enum_index)

    def _create(self):
        self.__create_annotation()
        self.__create_aim()
