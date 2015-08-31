#!/usr/bin/env python

"""
"""
# from link.util import vector
from maya import cmds

def match(target, source):
    """Match target to source xform"""
    match_translates(target, source)
    match_rotates(target, source)

def match_translates(move_node, target_node):
    """
    Match worldspace position
    """

    pos = cmds.xform(target_node, q=True, ws=True, t=True)
    set_translates(move_node, pos)

def set_translates(transform, array, world=True):
    cmds.xform(transform, t=array, ws=world, os=not world)    

def match_rotates(target, source):
    """Match worldspace rotate"""
    rot = cmds.xform(source, q=True, ws=True, ro=True)
    set_rotates(target, rot)

def set_rotates(transform, array, world=True):
    cmds.xform(transform, ro=array, ws=world, os=not world)

def match_pivot(target, source):
    rotate_translate_piv = cmds.xform(target, q=True, rp=True, ws=True)
    scale_piv = cmds.xform(target, q=True, sp=True, ws=True)
    cmds.xform(source, rp=rotate_translate_piv, ws=True)
    cmds.xform(source, sp=scale_piv, ws=True)

def match_average_position(target, sources):

    vectors = []
    for source in sources:
        vec3f = cmds.xform(source, q=True, ws=True, t=True)
        vectors.append(vec3f)

    average = vector.average_vector3f(vectors)
    cmds.xform(target, ws=True, t=average)
