#!/usr/bin/env python

"""
ass
"""

import os
import json
from maya import cmds
from crefor import decorators
from crefor.lib import libUtil, libXform, libName
from crefor.model.guide.guide import Guide

@decorators.name
def create(position, description, index=0):
    """create(position, description, index=0)
    Create a guide.

    :param      position:       L, R, C, etc
    :param      description:    Description of guide
    :param      index:          Index of guide
    :type       position:       str
    :type       description:    str
    :type       index:          int
    :returns:   Guide

    **Example**:

    >>> create("C", "spine", index=0)
    # Result: Guide(C_spine_0_gde) # 
    """

    return Guide(position=position,
                 description=description,
                 index=index).create()

def duplicate(guide, hierarchy=True):
    """create(position, description, index=0)
    Create a guide.

    :param      position:       Guide node
    :type       position:       Guide, str
    :returns:   Guide

    **Example**:

    >>> duplicate("C_spine_0_gde")
    # Result: Guide(C_spine_1_gde) # 
    """

    guide = __validate(guide)

    data = libUtil.write_hierarchy(guide)
    dup_data = {}

    # Create duplicate guides
    for parent in data:
        dup_parent = parent.duplicate()
        dup_data[parent] = dup_parent

    # Create duplicate hierarchy
    for parent in data:
        libXform.match_translates(dup_data[parent].joint, parent.joint)
        for child in data[parent]:
            dup_data[parent].add_child(dup_data[child])

    # Select top guide
    top_guide = dup_data.values().pop(0).joint
    while cmds.listRelatives(top_guide, parent=True):
        top_guide = cmds.listRelatives(top_guide, parent=True)[0]

    # Return duplicate nodes in list format
    # First index in list is top of hierarchy
    dup_guides = dup_data.values()
    dup_guides.insert(0, dup_guides.pop(dup_guides.index(Guide(*libName.decompile(top_guide, 3)))))

    cmds.select(dup_guides[0].joint, r=True)
    return dup_guides

def reinit(guide):
    """create(position, description, index=0)
    Create a guide.

    :param      position:       Guide node
    :type       position:       Guide, str
    :returns:   Guide

    **Example**:

    >>> duplicate("C_spine_0_gde")
    # Result: Guide(C_spine_1_gde) # 
    """

    guide = __validate(guide)
    return guide.reinit()

def set_parent(child, parent):
    """set_parent(child, parent)
    Set child guides parent.

    :param      parent:     Parent guide child will be added to.
    :param      child:      Child guide that will be added to parent.
    :type       parent:     str
    :type       child:      str
    :returns:   Parent guide

    **Example**:

    >>> set_parent("C_arm_0_gde", "C_spine_0_gde")
    # Result: Guide(C_spine_0_gde) # 
    """

    child = __validate(child)
    parent = __validate(parent)
    return child.set_parent(parent)

def add_child(parent, child):
    """add_child(parent, child)
    Add a child guide to parent guide

    :param      parent:     Parent guide child will be added to.
    :param      child:      Child guide that will be added to parent.
    :type       parent:     str
    :type       child:      str
    :rtype:                 crefor.model.guide.Guide

    **Example**:

    >>> add_child("C_arm_0_gde", "C_spine_0_gde")
    # Result: Guide(C_spine_0_gde) # 
    """

    child = __validate(child)
    parent = __validate(parent)
    return parent.add_child(child)

def has_parent(child, parent):
    """has_parent(child, parent)
    Does the child have parent anywhere in it's hierarchy?

    :param      child:      Guide that will checked
    :type       child:      str, Guide
    :rtype:                 bool

    **Example**:

    >>> has_parent("C_root_0_gde")
    # Result: False # 
    """

    child = __validate(child)
    parent = __validate(parent)
    return child.has_parent(parent)

def has_child(parent, child):
    """has_child(parent, child)
    Is guide an immediate child of parent?

    :param      parent:     Parent guide child will be added to.
    :param      child:      Child guide that will be added to parent.
    :type       parent:     str
    :type       child:      str
    :rtype:                 bool

    **Example**:

    >>> has_child("C_spine_0_gde", "C_arm_0_gde")
    # Result: True # 
    """

    child = __validate(child)
    parent = __validate(parent)
    return child.has_parent(parent)

def is_parent(parent, child):
    """is_parent(child, parent)
    Is guide the immediate parent of child?

    :param      parent:     Child guide that will check for parent
    :param      child:      Parent guide that will check for child
    :type       parent:     str
    :type       child:      str
    :rtype:                 bool

    **Example**:

    >>> is_parent("C_spine_0_gde", "C_arm_0_gde")
    # Result: True # 
    """

    child = __validate(child)
    parent = __validate(parent)
    return child.is_parent(parent)

def remove(guide):
    """remove(guide)
    Remove guide from scene

    :param      guide:      Guide to be removed
    :type       guide:      str, Guide

    **Example**:

    >>> remove("C_arm_0_gde")
    >>> cmds.ls("C_arm_0_gde")
    # Result: [] #
    """

    guide = __validate(guide)
    guide.remove()

def remove_parent(guide):
    """remove_parent(guide)
    Remove guides parent if available

    :param      guide:      Guide to be removed
    :type       guide:      str, Guide

    **Example**:

    >>> remove_parent("C_arm_0_gde")
    >>> cmds.listRelatives("C_arm_0_gde", parent=True, type="joint")
    # Result: [] #
    """

    guide = __validate(guide)
    guide.remove_parent()

def compile():
    """
    Compile all guides into joints.

    :type       child:      str
    :rtype:                 tuple
    :returns:               Tuple of compiled joints
    """

    guides = get_guides()

    # Create hierarchy
    hierarchy = {}
    for guide in guides:
        print guide, guide.children
        hierarchy[guide] = guide.children.values()

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

    return joints

def get_guides():
    """
    Get list of guides in scene

    :rtype:                 tuple
    :returns:               Tuple of guides
    """

    _guides = cmds.ls("*%s" % Guide.SUFFIX, type="joint")
    return [__validate(node) for node in _guides]

def exists(guide):
    """
    """

    try:

        # Exception is raised if guide does not exist
        guide = __validate(guide)
        return guide.exists()

    except Exception:
        return False

def set_axis(guide, axis="xyz"):
    """
    """

    guide.set_axis(axis)


def write(path="/Users/eddiehoyle/Python/creatureforge/examples/data/test.json", guides=[]):
    """
    Write out a json data snapshot of all guides

    :param      path:       Path where the data snapshot file is written to disk
    :param      guides:     List of guides whose data will be written to disk
    :type       path:       str
    :type       guides:     list
    :rtype:                 bool
    :returns:               If path exists on disk

    **Example**:

    >>> # Save all guides to disk
    >>> write("C:/documents/guides.json")
    >>> # Result: True #

    >>> # Write out only input guides
    >>> write("C:/documents/template.json", guides=["L_arm_0_gde"])
    >>> # Result: True #
    """

    # Get guides input or list from scene
    if guides:
        guides = [__validate(node) for node in guides]
    else:
        guides = get_guides()

    # Don't write file to disk of no guides are found
    if not guides:
        return False

    # Create a data snapshot dict of guide
    data = {}
    for guide in guides:
        data[guide.joint] = dict(children=guide.children.keys(),
                                parent=guide.parent.name if guide.parent else None,
                                xform=guide.get_translates(),
                                aim_at=guide.get_aim_at(),
                                axis=guide.get_axis())

    # Write file to disk
    try:
        with open(path, 'w') as f:
            f.write(json.dumps(data, indent=4))
    except Exception:
        raise

    return os.path.exists(path)

def read(path="/Users/eddiehoyle/Python/creatureforge/examples/data/test.json", compile_guides=False):
    """
    Load a data snapshot of guides and recreate

    :param      path:       Path where the data snapshot file is written to disk
    :param      compile:    Compile loaded snapshot into joints after
                            guides are recreated.
    :type       path:       str
    :type       compile:    bool
    :rtype:                 list
    :returns:               List of guides or joints created from snapshot

    **Example**:

    >>> read("C:/documents/guides.json")
    >>> # Result: ["L_arm_0_gde"] #

    >>> read("C:/documents/guides.json", compile=True)
    >>> # Result: ["L_arm_0_jnt"] #
    """

    data = {}

    try:
        with open(path, "rU") as f:
            data = json.loads(f.read())
    except Exception:
        raise

    # # Reini
    # _guides = {}
    # for key in data:
    #     _guides[__validate(guide)] = [__validate(g) for g in data[key]]

    # Check if all guides exist first
    for guide in data.keys():
        if not cmds.objExists(guide):
            raise NameError("Guide '%s' does not exist." % guide)

    # Set guides translates
    for guide in data.keys():
        guide = __validate(guide)
        guide.set_translates(data[guide.name]["xform"])

    # Create hierarchy, set aim targets
    for guide in data.keys():
        guide = __validate(guide)
        for child in data[guide.name]["children"]:
            child = __validate(child)
            add_child(guide, child)
            guide.set_axis(data[guide.name]["axis"])
        guide.aim_at(data[guide.name]["aim_at"])

    # Compile into joints
    if compile_guides:
        compile()

    return 

def rebuild(path="/Users/eddiehoyle/Python/creatureforge/examples/data/test.json", compile_guides=False):
    """
    Rebuild all guides from a snapshot

    :param      path:       Path where the data snapshot file is written to disk
    :param      compile:    Compile loaded snapshot into joints after
                            guides are recreated.
    :type       path:       str
    :type       compile:    bool
    :rtype:                 list
    :returns:               List of guides or joints created from snapshot

    **Example**:

    >>> rebuild("C:/documents/guides.json")
    >>> # Result: ["L_arm_0_gde"] #

    >>> rebuild("C:/documents/guides.json", compile=True)
    >>> # Result: ["L_arm_0_jnt"] #
    """

    data = {}

    try:
        with open(path, "rU") as f:
            data = json.loads(f.read())
    except Exception:
        raise

    for guide in data.keys():
        create(libName.decompile(guide, 3))

    read(path, compile_guides=compile_guides)


def __validate(guide):
    """
    Reinit a guide

    :param      guide:      Node to be reinitialised as guide
    :type       guide:      str
    :rytpe:                 Guide
    :returns:               Reinitialised guide model

    **Example**:

    >>> __validate("L_arm_0_gde")
    >>> # Result: <Guide "L_arm_0_gde"> #
    """
    if isinstance(guide, Guide):
        return guide
    else:
        return Guide(*libName.decompile(str(guide), 3)).reinit()
