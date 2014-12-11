#!/usr/bin/env python

'''
'''

import re
from maya import cmds

CONVENTION = '^((?!_)[a-zA-Z])_((?!_)[a-zA-Z0-9]+)_(\d+)_((?!_)[a-zA-Z]+)$'

def _decompile(name):
    try:
        return list(re.match(CONVENTION, name).groups())
    except AttributeError:
        raise NameError('Name does not match naming conventions: %s' % name)

def is_valid(name):
    try:
        return bool(_decompile(name))
    except Exception:
        return False


def create_name(position, description, index=0, suffix='grp'):
    return '_'.join(_decompile('_'.join([str(position),
                                        str(description),
                                        str(index),
                                        str(suffix)])))

def generate_name(position, description, index=0, suffix='grp'):
    name = create_name(position, description, index, suffix)
    while cmds.objExists(name):
        index += 1
        name = create_name(position, description, index, suffix)
    return name

def get_position(name):
    return _decompile(name)[0]

def get_description(name):
    return _decompile(name)[1]

def get_index(name):
    return int(_decompile(name)[2])

def get_suffix(name):
    return _decompile(name)[3]

def set_position(name, position):
    data = _decompile(name)
    data[0] = position
    return create_name(*data)

def set_description(name, position):
    data = _decompile(name)
    data[1] = position
    return create_name(*data)

def set_index(name, position):
    data = _decompile(name)
    data[2] = position
    return create_name(*data)

def set_suffix(name, position):
    data = _decompile(name)
    data[3] = position
    return create_name(*data)

def append_description(name, description):
    data = _decompile(name)
    data[1] = '%s%s' % (data[1], "%s%s" % (description[0].upper(), description[1:]))
    return create_name(*data)
