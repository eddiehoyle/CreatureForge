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
        data[guide] = guide.children
        for child in guide.children:
            recur(child, data)
    recur(guide, data)
    return data

def duplicate(guide, hierarchy=True):
    guide = validate(guide)

    data = get_hierarchy(guide)
    duplicate_data = {}
    other = defaultdict(list)

    # Store duplicate guides
    for parent in data:
        dup_parent = parent.copy()
        duplicate_data[dup_parent] = parent

    for dup_parent in duplicate_data:
        parent = duplicate_data[dup_parent]
        other[dup_parent] = []
        for child in data[parent]:
            other[dup_parent].append(dup_child)

    for parent in other:
        for child in other[parent]:
            parent.add_child(child)

    return other

    # dup_data = {}

    # # Create duplicate guides
    # for parent in data:
    #     dup_parent = parent.copy()
    #     dup_data[parent] = dup_parent

    # # Create duplicate hierarchy
    # for parent in data:
    #     libxform.match_translates(dup_data[parent].node, parent.node)
    #     for child in data[parent]:
    #         dup_data[parent].add_child(dup_data[child])

    # # Select top guide
    # print "dup_data", dup_data
    # top_guide = dup_data.values().pop(0).node
    # while cmds.listRelatives(top_guide, parent=True):
    #     top_guide = cmds.listRelatives(top_guide, parent=True)[0]

    # # Return duplicate nodes in list format
    # # First index in list is top of hierarchy
    # dup_guides = dup_data.values()
    # dup_guides.insert(0, dup_guides.pop(dup_guides.index(Guide(*libName.decompile(top_guide, 3)))))

    # cmds.select(dup_guides[0].node, r=True)

    # logger.info("Duplicate guides created: %s" % [g.node for g in dup_guides])
    # return dup_guides


def reinit(guide):
    guide = validate(guide)
    return guide.reinit()


def set_parent(child, parent):
    child = validate(child)
    parent = validate(parent)
    return child.set_parent(parent)


def add_child(parent, child):
    child = validate(child)
    parent = validate(parent)
    return parent.add_child(child)


def has_parent(child, parent):
    child = validate(child)
    parent = validate(parent)
    return child.has_parent(parent)


def has_child(parent, child):
    child = validate(child)
    parent = validate(parent)
    return child.has_parent(parent)


def is_parent(parent, child):
    child = validate(child)
    parent = validate(parent)
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
        hierarchy[guide] = guide.children

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
    _guides = cmds.ls("*%s" % Guide.SUFFIX, type="joint")

    guides = []
    for node in _guides:
        try:
            guides.append(validate(node))
        except Exception:
            logger.error("Failed to validate guide node: '%s'" % node)

    return guides


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
