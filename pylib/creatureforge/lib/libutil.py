#!/usr/bin/env python

"""
"""


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
