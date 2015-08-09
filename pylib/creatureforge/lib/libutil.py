#!/usr/bin/env python

"""
"""

import ast
import itertools
import collections

def stringify(dictionary):
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
