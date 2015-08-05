#!/usr/bin/env pythong

"""
Naming convention file

position_description(subType)_index_type
"""

import re
import logging

logging.basicConfig()
logger = logging.getLogger("__name__")

# ------------------------------------------------------------------------------

MAX = 4
DEFAULT_SUFFIX = "grp"

PATTERN_POSITION = "^([a-zA-Z]+)$"
PATTERN_DESCRIPTION = "^(?!^\d+)(?!^\d+$)([a-zA-Z0-9]+)$"
PATTERN_INDEX = "^(\d+)$"
PATTERN_SUFFIX = "^([a-zA-Z]+)$"

# ------------------------------------------------------------------------------


class InvalidNameException(Exception):
    pass


def validate(func):
    def wraps(*args, **kwargs):
        if not len(str(args[0]).split(NameHandler.SEP)) == MAX:
            err = "Invalid name: {name}".format(name=args[0])
            raise InvalidNameException(err)
        return func(*args, **kwargs)
    return wraps


class NameHandler(object):

    SEP = "_"

    def __init__(self, position, description, index, suffix):

        self.__set_position(position)
        self.__set_description(description)
        self.__set_index(index)
        self.__set_suffix(suffix)

    def __repr__(self):
            return self.compile()

    def compile(self):
        return ("{sep}".format(sep=NameHandler.SEP)).join([self.position,
                                                           self.description,
                                                           str(self.index),
                                                           self.suffix])

    def rename(self, position=None, description=None, index=None, suffix=None,
               append=None, **kwargs):
        if position is not None:
            self.position = position
        if description is not None:
            self.description = description
        if index is not None:
            self.index = index
        if suffix is not None:
            self.suffix = suffix
        if append is not None:
            self.description = self.__append_description(append)
        return self.compile()

    def __append_description(self, string):
        return "{description}{append}".format(
            description=self.description, append=string.title())

    def __match(self, pattern, value, err):
        try:
            return re.match(pattern, value).group(0)
        except (AttributeError, TypeError):
            raise InvalidNameException(err)

    def __set_position(self, val):
        err = "Invalid position: '{val}'".format(val=val)
        self.__position = str(self.__match(PATTERN_POSITION, val, err)).upper()

    def __set_description(self, val):
        err = "Invalid description: '{val}'".format(val=val)
        self.__description = self.__match(PATTERN_DESCRIPTION, val, err)

    def __set_index(self, val):
        err = "Invalid index: '{val}'".format(val=val)
        self.__index = int(self.__match(PATTERN_INDEX, str(val), err))

    def __set_suffix(self, val):
        err = "Invalid suffix: '{val}'".format(val=val)
        self.__suffix = self.__match(PATTERN_SUFFIX, val, err)

    def __get_position(self):
        return self.__position

    def __get_description(self):
        return self.__description

    def __get_index(self):
        return self.__index

    def __get_suffix(self):
        return self.__suffix

    def __get_tokens(self):
        return (self.position, self.description, self.index, self.suffix)

    # Properties
    position = property(fget=__get_position, fset=__set_position)
    description = property(fget=__get_description, fset=__set_description)
    index = property(fget=__get_index, fset=__set_index)
    suffix = property(fget=__get_suffix, fset=__set_suffix)
    tokens = property(fget=__get_tokens)


def create(position, description, index, suffix):
    return str(NameHandler(position, description, index, suffix))


def generate(position, description, index, suffix):
    pass
    # return str(NameHandler(position, description, index, suffix))


@validate
def decompile(name):
    return NameHandler(*name.split(NameHandler.SEP)).tokens


@validate
def rename(name, **kwargs):
    return NameHandler(*decompile(name)).rename(**kwargs)


@validate
def position(name):
    return NameHandler(*decompile(name)).position


@validate
def description(name):
    return NameHandler(*decompile(name)).description


@validate
def index(name):
    return NameHandler(*decompile(name)).index


@validate
def suffix(name):
    return NameHandler(*decompile(name)).suffix
