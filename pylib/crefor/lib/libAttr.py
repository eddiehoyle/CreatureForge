#!/usr/bin/env python

'''
General attribute use
'''

from maya import cmds

class MayaAttributeError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def add_separator(node, name):
    'Add a separator attr'
    add_enum(node, name, ['attributes'], False, True)


def add_long(node, kwargs):
    'Long attribute'
    attr = kwargs['ln']
    if _safe_attr(node, attr):
        full = '%s.%s' % (node, attr)
        cmds.addAttr(node, **kwargs)
    return full

def add_long2(node, name, keyable=True, channelBox=True):
    'Long attribute'
    attr = None
    if _safe_attr(node, name):
        attr = '%s.%s' % (node, name)
        cmds.addAttr(node, ln=name, at='long')
        cmds.setAttr(attr, cb=channelBox)
        cmds.setAttr(attr, k=keyable)
    return attr


def add_double():
    pass

def add_string(node, name, data=None, keyable=True, channelBox=True):
    'String attribute'
    attr = None
    if _safe_attr(node, name):
        attr = '%s.%s' % (node, name)
        cmds.addAttr(node, ln=name, dt='string')
        cmds.setAttr(attr, cb=channelBox)
        cmds.setAttr(attr, k=keyable)

        if data:
            cmds.setAttr(attr, data, type='string')

    return attr

def add_enum(node, name, enumNames=[], keyable=True, channelBox=True):
    'Enum attribute'
    attr = None
    if _safe_attr(node, name):
        attr = '%s.%s' % (node, name)
        cmds.addAttr(node, ln=name, at='enum', en=':'.join(enumNames))
        cmds.setAttr(attr, cb=channelBox)
        cmds.setAttr(attr, k=keyable)
    return attr


def hide_attr(node, attr):
    'Hides attr, still usable'
    cmds.setAttr('%s.%s' % (node, attr), k=False)
    cmds.setAttr('%s.%s' % (node, attr), cb=False)

def lock_attr(node, attr):
    'Lock attr, still visible'
    cmds.setAttr('%s.%s' % (node, attr), lock=True)

def unlock_attr(node, attr):
    '''Lock attr, still visible'''
    cmds.setAttr('%s.%s' % (node, attr), lock=False)

def nonkeyable_attr(node, attr):
    cmds.setAttr('%s.%s' % (node, attr), k=False)
    cmds.setAttr('%s.%s' % (node, attr), cb=True)

def hide_translates(node):
    for axis in ['X', 'Y', 'Z']:
        hide_attr(node, 'translate%s' % axis)

def hide_rotates(node):
    for axis in ['X', 'Y', 'Z']:
        hide_attr(node, 'rotate%s' % axis)

def hide_scales(node):
    for axis in ['X', 'Y', 'Z']:
        hide_attr(node, 'scale%s' % axis)

def lock_translates(node):
    'Lock translate individual attrs'
    for axis in ['X', 'Y', 'Z']:
        if _has_attr(node, 'translate%s' % axis):
            lock_attr(node, 'translate%s' % axis)

def lock_rotates(node):
    'Lock rotate individual attrs'
    for axis in ['X', 'Y', 'Z']:
        if _has_attr(node, 'rotate%s' % axis):
            lock_attr(node, 'rotate%s' % axis)

def lock_scales(node):
    'Lock scale individual attrs'
    for axis in ['X', 'Y', 'Z']:
        if _has_attr(node, 'scale%s' % axis):
            lock_attr(node, 'scale%s' % axis)

def lock_vis(node):
    'Lock visibility'
    if _has_attr(node, 'visibility'):
        lock_attr(node, 'visibility')

def hide_vis(node):
    'Hide visibility'
    if _has_attr(node, 'visibility'):
        hide_attr(node, 'visibility')

def nonkeyable_translates(node):
    for axis in ['X', 'Y', 'Z']:
        nonkeyable_attr(node, 'translate%s' % axis)

def nonkeyable_rotates(node):
    for axis in ['X', 'Y', 'Z']:
        nonkeyable_attr(node, 'rotate%s' % axis)

def nonkeyable_scales(node):
    for axis in ['X', 'Y', 'Z']:
        nonkeyable_attr(node, 'scale%s' % axis)

def lock_all(node):
    'Common lock all attrs'
    lock_translates(node)
    lock_rotates(node)
    lock_scales(node)
    hide_vis(node)

def _safe_attr(node, name):
    '''Raise error if attr already exists'''
    if _has_attr(node, name):
        raise MayaAttributeError('%s.%s attribute path already exists!' % (node, name))
    return True

def _has_attr(node, name):
    '''Check if input node has attribute'''
    return cmds.listAttr(node).count(name)