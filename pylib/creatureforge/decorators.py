#!/usr/bin/env python

from maya import cmds


def exists(func):
    def wraps(*args, **kwargs):
        if not cmds.objExists(str(args[0])):
            raise Exception("Nooo")
        return func(*args, **kwargs)
    return wraps
