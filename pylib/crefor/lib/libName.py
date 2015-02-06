#!/usr/bin/env python

'''
'''

import re
from maya import cmds
from copy import deepcopy

__all__ = ["compile", "update", "decompile"]

# This is not accurate enough. Fix!
CONVENTION = "^((?!_)[a-zA-Z])_((?!_)[a-zA-Z0-9]+)_(\d+)_((?!_)[a-zA-Z]+)$"


class __Name(object):
    """
    """

    SEP = "_"


    def __init__(self, position, description, index=0, suffix="grp"):

        self.position = position
        self.description = description
        self.index = index
        self.suffix = suffix

    def __getitem__(self, key):
        return self.decompile()[key]

    def __str__(self):
        return self.__compile()

    def __repr__(self):
        return self.__compile()

    def __eq__(self, other):
        return self.__compile() == str(other)

    def __get_position(self):
        return self.__position

    def __get_description(self):
        return self.__description

    def __get_index(self):
        return int(self.__index)

    def __get_suffix(self):
        return self.__suffix

    def __set_position(self, position):
        self.__position = self.__validate("^((?!_)[a-zA-Z]+)$", str(position)).upper()

    def __set_description(self, description):
        self.__description = self.__validate("^((?!_)[a-zA-Z0-9]+)$", str(description))

    def __set_index(self, index):
        self.__index = self.__validate("^((?!_)[0-9]+)$", str(index))

    def __set_suffix(self, suffix):
        self.__suffix = self.__validate("^((?!_)[a-zA-Z0-9]+)$", str(suffix))

    position = property(fget=__get_position, fset=__set_position)
    description = property(fget=__get_description, fset=__set_description)
    index = property(fget=__get_index, fset=__set_index)
    suffix = property(fget=__get_suffix, fset=__set_suffix)

    def __compile(self):
        return ("%s" % self.SEP).join([self.position,
                                       self.description,
                                       str(self.index),
                                       self.suffix])

    def __validate(self, regex, string):
        """
        """

        try:
            return re.match(regex, string).group(0)
        except AttributeError:
            raise ValueError("Invalid naming convention: %s" % string)

    def __append_description(self, string):
        """
        """

        if not string:
            return self.description

        if str(string)[0].isalpha():
            string = "%s%s" % (string[0].upper(), string[1:])

        return "%s%s" % (self.description, string)

    def update(self, position=None, description=None, index=None, suffix=None, **kwargs):
        """
        """

        if position:
            self.position = position if position else self.position

        if description:
            self.description = description

        if index:
            self.index = index

        if suffix:
            self.suffix = suffix

        if kwargs.get("append"):
            self.description = self.__append_description(kwargs["append"])

        return self

    def copy(self):
        return deepcopy(self)

    def compile(self):
        return self.__compile()

    def decompile(self, depth=None):
        return (self.position, self.description, self.index, self.suffix)[:depth]

    def recompile(self, *args, **kwargs):
        return str(self.copy().update(*args, **kwargs))

    def generate(self):
        new = self.copy()
        while cmds.objExists(new.compile()):
            new.index += 1
        return new.compile()

def compile(position, description, index, suffix):
    return __Name(position, description, index, suffix).compile()

def update(name, **kwargs):
    return __Name(*name.split(__Name.SEP)).recompile(**kwargs)

def decompile(name, depth=None):
    return __Name(*name.split(__Name.SEP)).decompile(depth)

def generate(name):
    return __Name(*decompile(name)).generate()

def is_valid(name):
    return len(name.split(__Name.SEP)) == 4

def position(name):
    return __Name(*name.split(__Name.SEP)).position

def description(name):
    return __Name(*name.split(__Name.SEP)).description

def index(name):
    return __Name(*name.split(__Name.SEP)).index

def suffix(name):
    return __Name(*name.split(__Name.SEP)).suffix
