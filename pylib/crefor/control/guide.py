#!/usr/bin/env python

"""
A module to create and manipulate guides. Functions
can accept both string or Guide objects as arguments
where required.
"""

import os
import json
from maya import cmds

from crefor.lib import libUtil, libXform, libName
from crefor.model.guide.guide import Guide

from crefor import log
logger = log.get_logger(__name__)

def create(position, description, index=0):
    """create(position, description, index=0)
    Create a guide.

    :param      position:       L, R, C, etc
    :type       position:       str
    :param      description:    Description of guide
    :type       description:    str
    :param      index:          Index of guide
    :type       index:          int
    :returns:                   Newly created guide
    :rtype:                     Guide

    **Example**:

    >>> create("C", "spine", index=0)
    # Result: <Guide 'C_spine_0_gde'> #
    """

    guide = Guide(position=position,
                  description=description,
                  index=index).create()
    return guide

def duplicate(guide, hierarchy=True):
    """duplicate(guide, hierarchy=True)
    Duplicate a guide. The duplicate guides names are all generated in scene
    to find the latest available index from input guide argument.

    :param      position:       Guide to duplicate from
    :type       position:       Guide, str
    :param      hierarchy:      Duplicate all decendents
    :type       hierarchy:      bool
    :returns:                   The new duplicate guides
    :rtype:                     list

    **Example**:

    >>> duplicate("C_spine_0_gde")
    # Result: <Guide 'C_spine_1_gde'> #
    """

    guide = validate(guide)

    data = libUtil.write_hierarchy(guide)
    dup_data = {}

    # Create duplicate guides
    for parent in data:
        dup_parent = parent.duplicate()
        dup_data[parent] = dup_parent

    # Create duplicate hierarchy
    for parent in data:
        libXform.match_translates(dup_data[parent].node, parent.node)
        for child in data[parent]:
            dup_data[parent].add_child(dup_data[child])

    # Select top guide
    top_guide = dup_data.values().pop(0).node
    while cmds.listRelatives(top_guide, parent=True):
        top_guide = cmds.listRelatives(top_guide, parent=True)[0]

    # Return duplicate nodes in list format
    # First index in list is top of hierarchy
    dup_guides = dup_data.values()
    dup_guides.insert(0, dup_guides.pop(dup_guides.index(Guide(*libName.decompile(top_guide, 3)))))

    cmds.select(dup_guides[0].node, r=True)

    logger.info("Duplicate guides created: %s" % [g.node for g in dup_guides])
    return dup_guides

def reinit(guide):
    """reinit(guide)
    Reinitialise a guide. This simply converts args to a Guide model object
    if the guide exists in the scene.

    :param      position:       Guide node
    :type       position:       Guide, str
    :returns:                   A Guide model object
    :rtype:                     Guide

    **Example**:

    >>> reinit("C_spine_0_gde")
    # Result: <Guide 'C_spine_0_gde'> #
    """

    guide = validate(guide)
    return guide.reinit()

def set_parent(child, parent):
    """set_parent(child, parent)
    Set child guides parent.

    :param      child:      Child guide that will be added to parent.
    :type       child:      Guide, str
    :param      parent:     Parent guide child will be added to.
    :type       parent:     Guide, str
    :returns:               Parent guide
    :rtype:                 Guide

    **Example**:

    >>> set_parent("C_arm_0_gde", "C_spine_0_gde")
    # Result: <Guide 'C_spine_0_gde'> #
    """

    child = validate(child)
    parent = validate(parent)
    return child.set_parent(parent)

def add_child(parent, child):
    """add_child(parent, child)
    Add a child guide to parent guide

    :param      parent:     Parent guide child will be added to.
    :type       parent:     Guide, str
    :param      child:      Child guide that will be added to parent.
    :type       child:      Guide, str
    :returns:               Child guide
    :rtype:                 Guide

    **Example**:

    >>> add_child("C_arm_0_gde", "C_spine_0_gde")
    # Result: Guide(C_spine_0_gde) # 
    """

    child = validate(child)
    parent = validate(parent)
    return parent.add_child(child)

def has_parent(child, parent):
    """has_parent(child, parent)
    Does the child have parent anywhere in it's hierarchy?

    :param      child:      Guide that will checked
    :type       child:      str, Guide
    :returns:               If the parent guide is a parent anywhere above the
                            child guide.
    :rtype:                 bool

    **Example**:

    >>> # Is C_root_0_gde above C_spine_3_gde in hierarchy?
    >>> has_parent("C_spine_3_gde", "C_root_0_gde")
    # Result: True # 
    """

    child = validate(child)
    parent = validate(parent)
    return child.has_parent(parent)

def has_child(parent, child):
    """has_child(parent, child)
    Is guide an immediate child of parent?

    :param      parent:     Parent guide child will be added to.
    :param      child:      Child guide that will be added to parent.
    :type       parent:     str
    :type       child:      str
    :returns:               Is child guide an immediate child of the parent guide?
    :rtype:                 bool

    **Example**:

    >>> # Is L_arm_1_gde an immediate child of L_arm_0_gde?
    >>> has_child("L_arm_0_gde", "L_arm_1_gde")
    # Result: True # 
    """

    child = validate(child)
    parent = validate(parent)
    return child.has_parent(parent)

def is_parent(parent, child):
    """is_parent(parent, child)
    Is parent guide an immediate parent of the child guide?

    :param      parent:     Child guide that will check for parent
    :param      child:      Parent guide that will check for child
    :type       parent:     str
    :type       child:      str
    :returns:               If child guide's parent is the parent guide
    :rtype:                 bool

    **Example**:

    >>> is_parent("C_spine_0_gde", "C_arm_0_gde")
    # Result: True # 
    """

    child = validate(child)
    parent = validate(parent)
    return child.is_parent(parent)

def remove(guide):
    """remove(guide)
    Delete the guide from the scene

    :param      guide:      Guide to be removed
    :type       guide:      str, Guide

    **Example**:

    >>> remove("C_arm_0_gde")
    >>> cmds.ls("C_arm_0_gde")
    # Result: [] #
    """

    guide = validate(guide)

    cmds.undoInfo(openChunk=True)
    guide.remove()
    cmds.undoInfo(closeChunk=True)

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

    guide = validate(guide)
    guide.remove_parent()

def compile():
    """
    Compile all guides into joints.

    :returns:               Tuple of compiled joints
    :rtype:                 tuple

    **Example**:

    >>> spine = create("C", "spine", index=0)
    # Result: <Guide 'C_spine_0_gde'> #
    >>> compile()
    # Result ("C_spine_0_jnt", ) #
    """

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
    """decompile()
    Convert all joints back to guides

    Problems that need solving:
        1. Use the same I/O logic for write/read to store snapshot
        2. Some math might be needed to determine aimAt target,
           burn in data to joint?

    """

    logger.warn("Decompile not implemented yet.")
    # joints = []
    # for joint in cmds.ls(type="joint"):
    #     if libName.is_valid(joint):
    #         joints.append(joint)

    # if joints:

    #     hierarchy = {}
    #     for joint in joints:
    #         hierarchy[joint] = cmds.listRelatives(joint, children=True) or []

    #     cmds.delete(joints)

    #     guide_hierarchy = {}
    #     for joint in hierarchy:
    #         guide = create(*libName.decompile(joint, 3))
    #         guide_hierarchy[guide] = []

    #         for child in hierarchy[joint]:
    #             child = create(*libName.decompile(child, 3))
    #             guide_hierarchy[guide].append(child)

    #     for guide in guide_hierarchy:
    #         for child in guide_hierarchy[guide]:
    #             child.set_parent(child)

def get_guides():
    """get_guides()
    Get all guides in scene

    :rtype:                 tuple
    :returns:               Tuple of guides
    """

    _guides = cmds.ls("*%s" % Guide.SUFFIX, type="joint")

    guides = []
    for node in _guides:
        try:
            guides.append(validate(node))
        except Exception:
            logger.error("Failed to validate guide node: '%s'" % node)

    return guides

def exists(guide):
    """exists(guide)
    Does the guide exist?

    :param      child:      Guide that will checked
    :type       child:      Guide, str
    :returns:               If the guide exists
    :rtype:                 bool
    """

    try:

        # Exception is raised if guide does not exist
        guide = validate(guide)
        return guide.exists()

    except Exception:
        return False

def set_axis(guide, primary="X", secondary="Y"):
    """set_axis(guide, primary="X", secondary="Y")
    Set the primary and secondary for joint orientation

    :param      child:          Guide that will checked
    :type       child:          str, Guide
    :param      primary:        Aim axis
    :type       primary:        str
    :param      seconday:       Up axis
    :type       seconday:       str
    """

    guide.set_axis(primary, secondary)

def set_orient(guide, vector3f=[0.0, 0.0, 0.0]):
    """
    """

    pass

def write(path, guides=[]):
    """write(path, guides=[])
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
    # Result: True #

    >>> # Write out only input guides
    >>> write("C:/documents/template.json", guides=["L_arm_0_gde"])
    # Result: True #
    """

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
    """read(path, compile_guides=False)
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
    # Result: ["L_arm_0_gde"] #

    >>> read("C:/documents/guides.json", compile=True)
    # Result: ["L_arm_0_jnt"] #
    """

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

        guide.set_position(snapshot["position"], local=False)
        guide.set_axis(snapshot["primary"], snapshot["secondary"])

    # Create hierarchy
    for guide, snapshot in data.items():
        guide = validate(guide)
        for child in snapshot["children"]:
            child = validate(child)
            add_child(guide, child)

        guide.up.set_position(snapshot["up_position"], local=False)

        guide.aim_flip(snapshot["aim_flip"])
        guide.aim_at(snapshot["aim_at"])

    # Compile into joints
    if compile_guides:
        compile()

    return 

def rebuild(path, compile_guides=False):
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
    # Result: ["L_arm_0_gde"] #

    >>> rebuild("C:/documents/guides.json", compile=True)
    # Result: ["L_arm_0_jnt"] #
    """

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
    """
    Reinit a guide

    :param      guide:      Node to be reinitialised as guide
    :type       guide:      str
    :rytpe:                 Guide
    :returns:               Reinitialised guide model

    **Example**:

    >>> validate("L_arm_0_gde")
    # Result: <Guide "L_arm_0_gde"> #
    """

    return Guide.validate(guide)
