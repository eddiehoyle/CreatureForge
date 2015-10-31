#!/usr/bin/env python

"""
Name model control, handles all intramodel functionality
"""

def set_parent(self, guide):
    raise NotImplementedError("set_parent")

def add_child(self, guide):
    raise NotImplementedError("add_child")

def remove_parent(self):
    raise NotImplementedError("remove_parent")

def remove_child(self, guide):
    raise NotImplementedError("remove_child")

def remove(self):
    raise NotImplementedError("remove")

def set_aim_flip(self, flip):
    raise NotImplementedError("set_aim_flip")

def set_aim_at(self, guide):
    raise NotImplementedError("set_aim_at")

def set_aim_orient(self, order):
    raise NotImplementedError("set_aim_orient")

def set_debug(self, debug):
    raise NotImplementedError("set_debug")

def set_offset_orient(self, x=None, y=None, z=None):
    raise NotImplementedError("set_offset_orient")

def set_translates(self, x, y, z, worldspace=False):
    raise NotImplementedError("set_translates")
