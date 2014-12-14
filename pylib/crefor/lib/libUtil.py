#!/usr/bin/env python

"""
Utility methods
"""

from maya import cmds
from crefor.lib import libName
from crefor.model.guide.guide import Guide

def write_hierarchy(guide):
    """
    Simple hierarchy data structure

    :param      position:       Guide node
    :type       position:       Guide, str
    :returns:   Guide

    **Example**:

    >>> write_hierarchy("C_spine_0_gde")
    """

    if isinstance(guide, Guide):
        guide = guide.joint

    data = {}
    all_guides = cmds.listRelatives(guide, allDescendents=True, type="joint") or []
    all_guides.insert(0, guide)
    for guide in all_guides:
        children = [Guide(*libName._decompile(c)[:-1]).reinit() for c in cmds.listRelatives(guide, children=True, type="joint") or []]
        guide = Guide(*libName._decompile(guide)[:-1]).reinit()

        data[guide] = children
    return data

def write_hierarchy_recursive(guide):
    guide = api.reinit(guide)
    def recur(guide):
        guide = api.reinit(guide)
        hierarchy = {}
        for child in cmds.listRelatives(guide.joint, children=True, type="joint") or []:
            child = api.reinit(child)
            hierarchy[child] = recur(child)
        return hierarchy
    return {guide: recur(guide)}

def read_hierarchy_recursive(data):
    def recur(data):
        for guide in data.keys():
            recur(data[guide])
        return data
    return recur(data)
