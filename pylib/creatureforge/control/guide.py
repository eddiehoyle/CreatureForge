#!/usr/bin/env python

"""
A module to create and manipulate guides. Functions
can accept both string or Guide objects as arguments
where required.
"""

import os
import json
import logging
from copy import deepcopy
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
    raise NotImplementedYet("Decompile not implemented yet.")


def get_guides():
    dags = cmds.ls("*%s" % Guide.SUFFIX, type="joint")
    guides = []
    for node in dags:
        try:
            guides.append(validate(node))
        except Exception:
            logger.error("Failed to validate guide node: '{node}'".format(
                node=node))
    return tuple(guides)


def exists(guide):
    try:

        # Exception is raised if guide does not exist
        guide = validate(guide)
        return guide.exists()

    except Exception:
        return False


def set_axis(guide, primary="X", secondary="Y"):
    guide.set_axis(primary, secondary)


def set_debug(value):
    guides = get_guides()
    for g in guides:
        g.set_debug(value)


def write(path, guides=[]):
    # Get guides input or list from scene
    if guides:

        guides = []
        for node in guides:
            try:
                guides.append(validate(node))
            except Exception:
                logger.error("Failed to validate guide node: '%s'" % node)

    else:
        guides = get_guides()

    # Don't write file to disk of no guides are found
    if not guides:
        return False

    # Create a data snapshot dict of guide
    data = {}
    for guide in guides:
        data[guide.node] = guide.snapshot()

    # Write file to disk
    try:
        with open(path, 'w') as f:
            f.write(json.dumps(data, indent=4))
    except Exception:
        raise

    return os.path.exists(path)


def read(path, compile_guides=False):
    data = {}

    try:
        with open(path, "rU") as f:
            data = json.loads(f.read())
    except Exception:
        raise

    # Check if all guides exist first
    for guide in data.keys():
        if not cmds.objExists(guide):
            raise NameError("Guide '%s' does not exist." % guide)

    # Setup behaviour
    for guide, snapshot in data.items():
        guide = validate(guide)

        guide.set_position(*snapshot["position"], worldspace=True)
        guide.set_axis(snapshot["primary"], snapshot["secondary"])

    # Create hierarchy
    for guide, snapshot in data.items():
        guide = validate(guide)
        for child in snapshot["children"]:
            child = validate(child)
            add_child(guide, child)

        guide.up.set_position(snapshot["up_position"], worldspace=True)

        guide.aim_flip(snapshot["aim_flip"])
        guide.aim_at(snapshot["aim_at"])
        guide.set_offset(*snapshot["offset"])

    # Compile into joints
    if compile_guides:
        compile()

    return 


def rebuild(path, compile_guides=False):
    cmds.undoInfo(openChunk=True)

    data = {}

    try:
        with open(path, "rU") as f:
            data = json.loads(f.read())
    except Exception:
        raise

    for guide in data.keys():
        create(*libName.decompile(guide, 3))

    read(path, compile_guides=compile_guides)

    cmds.undoInfo(closeChunk=True)


def validate(guide):
    return Guide.validate(guide)
