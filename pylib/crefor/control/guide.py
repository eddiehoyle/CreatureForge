#!/usr/bin/env python

"""
ass
"""

from functools import wraps
from crefor import decorators
from crefor.lib import libName
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

@decorators.guides
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

    return child.set_parent(parent)

@decorators.guides
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

    return parent.add_child(child)

@decorators.guides
def has_parent(guide):
    """has_parent(child, parent)
    Does the child have parent anywhere in it's hierarchy?

    :param      guide:      Guide that will checked
    :type       guide:      str, Guide
    :rtype:                 bool

    **Example**:

    >>> has_parent("C_root_0_gde")
    # Result: False # 
    """

    return bool(child.parent)

@decorators.guides
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

    return child.has_parent(parent)

@decorators.guides
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

    return parent.is_parent(child)

@decorators.guides
def remove(guide):
    """remove(guide)
    Remove guide from scene

    :param      guide:      Guide to be removed
    :type       guide:      str, Guide

    **Example**:

    >>> remove("C_arm_0_gde")
    >>> cmds.ls("C_arm_0_gde")
    # Result: False #
    """

    guide.remove()

@decorators.guides
def remove_parent(guide):
    """remove_parent(guide)
    Remove guides parent if available

    Remove guide from scene

    :param      guide:      Guide to be removed
    :type       guide:      str, Guide

    **Example**:

    >>> remove_parent("C_arm_0_gde")
    >>> cmds.ls("C_arm_0_gde")
    # Result: False #
    """

    guide.remove_parent()