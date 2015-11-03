#!/usr/bin/env python

from maya import cmds

"""
Maya utility methods
"""


class Selection(object):
    """Context manager to restore selection
    """

    def __init__(self):
        self.__selected = []

    def __enter__(self):
        self.__selected = cmds.ls(sl=True)

    def __exit__(self, exc_type, exc_value, traceback):
        cmds.select(self.__selected)
