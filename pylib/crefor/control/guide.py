#!/usr/bin/env python

"""
User guide interaction
"""

from crefor import decorators
from crefor.lib import libName, libShader, libAttr
from crefor.model.guide.guide import Guide

class NodeException(Exception):
    pass


def guides(func):
    """
    Guide validation decorator
    """

    def inner(*args, **kwargs):
        try:
            args = [Guide(*libName._decompile(arg)[:-1]).reinit() for arg in args]
        except Exception as e:

            raise NodeException("Error: %s" % e)
        return func(*args, **kwargs)
    return inner

@decorators.name
def create(position, description, index=0):
    """
    """

    return Guide(position=position,
                 description=description,
                 index=index).create()

@guides
def set_parent(child, parent):
    """
    """
    return child.set_parent(parent)

@guides
def add_child(parent, child):
    """
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