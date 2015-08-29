#!/usr/bin/env python

"""
A module to create and manipulate guides. Functions
can accept both string or Guide objects as arguments
where required.
"""

import os
import json
import logging
import traceback
from copy import deepcopy
from pprint import pprint
from collections import defaultdict

from maya import cmds

from creatureforge.lib import libutil
from creatureforge.lib import libxform
from creatureforge.lib import libname
from creatureforge.model.guide import Guide

logger = logging.getLogger(__name__)


def create(position, description, index=0):
    guide = Guide(position=position,
                  description=description,
                  index=index)
    guide.create()
    return guide


def get_hierarchy(guide):
    guide = Guide.validate(guide)
    data = {}
    def recur(guide, data):
        data[guide] = guide.get_children()
        for child in guide.get_children():
            recur(child, data)
    recur(guide, data)
    return data


def duplicate(guide, hierarchy=True):

    # Define containers
    guide = validate(guide)
    guides = get_hierarchy(guide)
    copy_guides = {}
    duplicates = []

    # Copy guides and store correlation
    for parent in guides:
        dup_parent = parent.copy()
        copy_guides[parent] = dup_parent
        duplicates.append(dup_parent)

    # Set hierarchy and positions
    for parent in guides:
        translates = parent.get_translates(worldspace=True)
        dup_parent = copy_guides[parent]
        dup_parent.set_translates(*translates, worldspace=True)
        for child in guides[parent]:
            dup_child = copy_guides[child]
            dup_parent.add_child(dup_child)

    # Select top of duplicate guides
    cmds.select(duplicates[0], replace=True)

    return duplicates


def set_parent(child, parent):
    parent = validate(parent)
    child = validate(child)
    child.set_parent(parent)


def add_child(parent, child):
    parent = validate(parent)
    child = validate(child)
    parent.add_child(child)


def add_children(parent, children):
    parent = validate(parent)
    for child in children:
        parent.add_child(child)


def has_parent(child, parent):
    parent = validate(parent)
    child = validate(child)
    return child.has_parent(parent)


def has_child(parent, child):
    parent = validate(parent)
    child = validate(child)
    return parent.has_child(child)


def is_parent(parent, child):
    parent = validate(parent)
    child = validate(child)
    return child.is_parent(parent)


def remove(guide):
    guide = validate(guide)

    cmds.undoInfo(openChunk=True)
    guide.remove()
    cmds.undoInfo(closeChunk=True)


def remove_parent(guide):
    guide = validate(guide)
    guide.remove_parent()


def compile():
    guides = get_guides()

    # Create hierarchy
    hierarchy = {}
    for guide in guides:
        hierarchy[guide] = guide.get_children()

    # Create joints
    joints = {}
    for guide in hierarchy:
        joint = guide.compile()
        joints[guide] = joint

    # Create joint hierarchy
    for guide in joints:
        for child in hierarchy[guide]:
            cmds.parent(joints[child], joints[guide])

    # Remove guides
    for guide in guides:
        guide.remove()

    return joints.values()


def decompile():
    raise NotImplementedError("Decompile not implemented yet.")


def get_guides():
    pattern = "*{suffix}".format(suffix=Guide.SUFFIX)
    joints = cmds.ls(pattern, type="joint")
    guides = []
    for node in joints:
        try:
            guides.append(validate(node))
        except Exception:
            logger.error("Failed to validate guide node: '{node}'".format(
                node=node))
    return tuple(guides)


def exists(guide):
    try:
        return validate(guide).exists()
    except Exception:
        return False


def set_aim_orient(guide, order):
    guide = validate(guide)
    guide.set_aim_orient(order)


def get_aim_orient(guide):
    guide = validate(guide)
    return guide.get_aim_orient()


def set_debug(guide, debug):
    guide = validate(guide)
    guide.set_debug(debug)


def write(guides, path):
    # Get guides input or list from scene
    _guides = []
    for node in guides:
        try:
            _guides.append(validate(node))
        except Exception:
            print("Failed to validate guide node: '%s'" % node)

    # Create a data snapshot dict of guide
    data = {}
    for guide in _guides:
        data[guide.get_node()] = guide.get_snapshot()

    # Write file to disk
    try:
        with open(path, 'w') as f:
            f.write(json.dumps(data, indent=4))
    except (OSError, IOError) as excp:
        err = "Failed to save path: {tb}".format(
            tb=traceback.format_exc(excp))
        logger.error(err)
        raisew

    return os.path.exists(path)


def read(path):
    try:
        with open(path, "rU") as f:
            return json.loads(f.read())
    except (OSError, IOError) as excp:
        err = "Failed to read snapshot path: {path}".format(
            path)
        logger.error(err)
        raise


def restore(path):

    data = read(path)

    # TODO:
    #   Raise warnings if snapshot targets don't exist

    # Setup behaviour
    for guide, snapshot in data.items():
        guide = validate(guide)
        guide.set_translates(*snapshot["translates"], worldspace=True)
        # guide.set_aim_axis(snapshot["primary"], snapshot["secondary"])

    # Create hierarchy
    for guide, snapshot in data.items():
        guide = validate(guide)
        for child in snapshot["children"]:
            child = validate(child)
            add_child(guide, child)

        guide.get_up().set_translates(*snapshot["up_translates"], worldspace=True)
        guide.set_aim_flip(snapshot["aim_flip"])

        if snapshot["aim_at"]:
            guide.set_aim_at(snapshot["aim_at"])

        # TODO:
        #   Rename this as 'orient_offset' and all things related
        guide.set_offset_orient(*snapshot["offset_orient"])


def rebuild(path):

    cmds.undoInfo(openChunk=True)

    for name in read(path).keys():
        create(*libname.tokens(name))

    restore(path)

    cmds.undoInfo(closeChunk=True)


def validate(guide):
    return Guide.validate(guide)
