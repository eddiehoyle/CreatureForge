#!/usr/bin/env python

"""
General attribute use
"""

from maya import cmds
from copy import deepcopy

class MayaAttribute(object):
    """
    Maya add, set and get attribute wrapper
    """

    DEFAULT = {}

    def __init__(self, node, name, *args, **kwargs):

        self.node = node
        self.name = name
        self.path = "%s.%s" % (self.node, self.name)

        self.args = args
        self.kwargs = deepcopy(kwargs)
        self.kwargs.update(self.DEFAULT)

    def has(self):
        return cmds.objExists(self.path)

    def add(self):
        if not self.has():
            cmds.addAttr(self.node, ln=self.name, *self.args, **self.kwargs)

    def set(self):
        if self.has():
            cmds.setAttr(self.path, *self.args, **self.kwargs)

    def edit(self):
        if self.has():
            cmds.addAttr(self.path, edit=True, *self.args, **self.kwargs)

    def lock(self):
        if self.has():
            cmds.setAttr(self.path, lock=True)

def add_double(node, name, *args, **kwargs):
    MayaAttribute(node, name, at="double", *args, **kwargs).add()

def add_long(node, name, *args, **kwargs):
    MayaAttribute(node, name, at="long", *args, **kwargs).add()

def add_bool(node, name, *args, **kwargs):
    MayaAttribute(node, name, at="bool", *args, **kwargs).add()

def add_string(node, name, *args, **kwargs):
    MayaAttribute(node, name, dt="string", *args, **kwargs).add()

def add_enum(node, name, enums=[], *args, **kwargs):
    MayaAttribute(node, name, at="enum", enumName=":".join(enums), *args, **kwargs).add()

def edit_enum(node, name, enums=[], *args, **kwargs):
    MayaAttribute(node, name, at="enum", enumName=":".join(enums), *args, **kwargs).edit()

def lock_translates(node, keyable=False, channelBox=False, *args, **kwargs):
    for axis in ["X", "Y", "Z"]:
        MayaAttribute(node, "translate%s" % axis, *args, **kwargs).set()

def lock_rotates(node, keyable=False, channelBox=False, *args, **kwargs):
    for axis in ["X", "Y", "Z"]:
        MayaAttribute(node, "rotate%s" % axis, *args, **kwargs).set()

def lock_scales(node, keyable=False, channelBox=False, *args, **kwargs):
    for axis in ["X", "Y", "Z"]:
        MayaAttribute(node, "scale%s" % axis, *args, **kwargs).set()

def lock_vis(node, keyable=False, channelBox=False, *args, **kwargs):
    MayaAttribute(node, "visibility", *args, **kwargs).set()

def lock_all(node, *args, **kwargs):
    lock_translates(node, *args, **kwargs)
    lock_rotates(node, *args, **kwargs)
    lock_scales(node, *args, **kwargs)
    lock_vis(node, *args, **kwargs)

def set_keyable(node, name, **kwargs):
    MayaAttribute(node, name, channelBox=True, **kwargs).set()
    MayaAttribute(node, name, keyable=True, **kwargs).set()

def set(node, name, *args, **kwargs):
    MayaAttribute(node, name, *args, **kwargs).set()

def add(node, name, *args, **kwargs):
    MayaAttribute(node, name, *args, **kwargs).add()

def edit(node, name, *args, **kwargs):
    MayaAttribute(node, name, *args, **kwargs).edit()

def has(node, name, *args, **kwargs):
    MayaAttribute(node, name, *args, **kwargs).has()

def lock(node, name, *args, **kwargs):
    MayaAttribute(node, name, *args, **kwargs).lock()