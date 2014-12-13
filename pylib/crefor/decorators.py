#!/usr/bin/env python

"""
"""

from crefor.lib import libName
from crefor.model.guide.guide import Guide
from crefor.exceptions import NodeException
from functools import wraps

def name(func):
    """name(func)
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

def guides(func):
    """guides(func)
    Guide validation decorator
    """

    @wraps(func)
    def inner(*args, **kwargs):
        try:
            args = [Guide(*libName._decompile(str(guide))[:-1]).reinit() for guide in args]
        except Exception as e:
            raise NodeException("Error: %s" % e)
        return func(*args, **kwargs)
    return inner