#!/usr/bin/env python

"""
"""

import ast
import itertools
import collections

def stringify(dictionary):
    """Turn all dict items into strings"""
    for key, value in dictionary.iteritems():
        if isinstance(value, dict):
            return stringify(value)
        elif isinstance(value, (set, tuple, list)):
            dictionary[key] = map(str, value)
        elif isinstance(value, bool):
            pass
        else:
            dictionary[key] = str(value)
    return dictionary


def flatten(l):
    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, basestring):
            for sub in flatten(el):
                yield sub
        else:
            yield el

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
