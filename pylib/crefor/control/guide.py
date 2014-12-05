#!/usr/bin/env python

"""
ass
"""

from functools import wraps
from crefor import decorators
from crefor.lib import libName
from crefor.model.guide.guide import Guide

class NodeException(Exception):
    pass


def guides(func):
    """
    Guide validation decorator
    """

    @wraps(func)
    def inner(*args, **kwargs):
        try:
            args = [Guide(*libName._decompile(arg)[:-1]).reinit() for arg in args]
        except Exception as e:

            raise NodeException("Error: %s" % e)
        return func(*args, **kwargs)
    return inner

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
    True
    """

    return Guide(position=position,
                 description=description,
                 index=index).create()

@guides
def set_parent(child, parent):
    """set_parent(child, parent)
    Set child guides parent.

    :param      parent:     Parent guide child will be added to.
    :param      child:      Child guide that will be added to parent.
    :type       parent:     str
    :type       child:      str
    :returns:   Guide

    **Example**:

    >>> set_parent("C_arm_0_gde", "C_spine_0_gde")
    True
    """

    return child.set_parent(parent)

@guides
def add_child(parent, child):
    """add_child(parent, child)
    Add a child guide to parent guide

    :param      parent:     Parent guide child will be added to.
    :param      child:      Child guide that will be added to parent.
    :type       parent:     str
    :type       child:      str
    :returns:   Guide

    **Example**:

    >>> add_child("C_arm_0_gde", "C_spine_0_gde")
    True
    """

    return parent.add_child(child)

@guides
def has_parent(child, parent):
    """
    """

    return child.has_parent(parent)

@guides
def has_child(parent, child):
    """
    """

    return child.has_parent(parent)

@guides
def is_parent(child, parent):
    """
    """

    return parent.is_parent(child)

@guides
def remove_guide(guide):
    """
    """

    return guide.remove()