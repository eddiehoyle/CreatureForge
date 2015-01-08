#!/usr/bin/env python

"""
Utility methods
"""

from maya import cmds
from crefor.model.guide.guide import Guide
from crefor import log

logger = log.get_logger(__name__)

def write_hierarchy(guide):
    """
    Simple hierarchy data structure

    :param      position:       Guide node
    :type       position:       Guide, str
    :returns:   Guide

    **Example**:

    >>> write_hierarchy("C_spine_0_gde")
    """
    try:
        guide = guide.joint
    except Exception:
        guide = str(guide)

        if not cmds.objExists(guide):
            raise NameError("'%s' is not a guide." % guide)

    data = {}
    all_guides = cmds.listRelatives(guide, allDescendents=True, type="joint") or []
    all_guides.insert(0, guide)
    for guide in all_guides:
        children = [Guide.validate(c) for c in cmds.listRelatives(guide, children=True, type="joint") or []]
        guide = Guide.validate(guide)

        data[guide] = children
    return data

def write_hierarchy_recursive(guide):
    guide = Guide.validate(guide)
    def recur(guide):
        guide = Guide.validate(guide)
        hierarchy = {}
        for child in cmds.listRelatives(guide.joint, children=True, type="joint") or []:
            child = Guide.validate(child)
            hierarchy[child] = recur(child)
        return hierarchy
    return {guide: recur(guide)}

def read_hierarchy_recursive(data):
    def recur(data):
        for guide in data.keys():
            recur(data[guide])
        return data
    return recur(data)
