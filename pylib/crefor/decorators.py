#!/usr/bin/env python

"""
"""

from crefor.lib import libName
from functools import wraps

def name(func):
    """
    Node name validation
    """

    @wraps(func)
    def inner(*args, **kwargs):
        try:
            libName.is_valid(libName.create_name(args[0], args[1], args[2]))
        except Exception:
            raise Exception("Bad name arguments: %s, %s" % (args, kwargs))
        return func(*args, **kwargs)
    return inner

def test(ass):
    """This function translates foo into bar

    :param ass: A string to be converted
    :returns: A bar formatted string
    """
    return ass