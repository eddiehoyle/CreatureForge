#!/usr/bin/env python

"""
"""

from crefor.lib import libName

def name(func):
    """
    Node name validation
    """

    def inner(*args, **kwargs):
        try:
            libName.is_valid(libName.create_name(args[0], args[1], args[2]))
        except Exception:
            raise Exception("Bad name arguments: %s, %s" % (args, kwargs))
        return func(*args, **kwargs)
    return inner