#!/usr/bin/env pythong

"""
Naming convention file

position_description(subType)_index_type
"""

import re
import logging
from copy import deepcopy

from creatureforge.exceptions import InvalidNameError

from maya import cmds

logging.basicConfig()
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------

MAX = 6
DEFAULT_SUFFIX = "grp"

PATTERN_POSITION = "^([a-zA-Z]+)$"
PATTERN_DESCRIPTION = "^(?!^\d+)(?!^\d+$)([a-zA-Z0-9]+)$"
PATTERN_INDEX = "^(\d+)$"
PATTERN_SUFFIX = "^([a-zA-Z]+)[\d+]?$"

# ------------------------------------------------------------------------------


def validate(func):
    def wraps(*args, **kwargs):
        if not len(str(args[0]).split(NameModel.SEP)) == MAX:
            err = "Invalid name: {name}".format(name=args[0])
            raise InvalidNameError(err)
        return func(*args, **kwargs)
    return wraps


class NameModel(object):

    SEP = "_"

    def __init__(self, position, primary, primary_index, secondary,
                 secondary_index, suffix):

        self.__set_position(position)
        self.__set_primary(primary)
        self.__set_primary_index(primary_index)
        self.__set_secondary(secondary)
        self.__set_secondary_index(secondary_index)
        self.__set_suffix(suffix)

    def __str__(self):
        return self.compile()

    def __repr__(self):
            return "<{cls} '{name}'>".format(
                cls=self.__class__.__name__,
                name=self.compile())

    @property
    def position(self):
        return self.__position

    @property
    def primary(self):
        return self.__primary

    @property
    def primary_index(self):
        return self.__primary_index

    @property
    def secondary(self):
        return self.__secondary

    @property
    def secondary_index(self):
        return self.__secondary_index

    @property
    def suffix(self):
        return self.__suffix

    def tokenize(self):
        return self.get_components()[:-1]

    def get_components(self):
        return [self.position,
                self.primary,
                str(self.primary_index),
                self.secondary,
                str(self.secondary_index),
                self.suffix]

    def get_data(self):
        return {"position": self.position,
                "primary": self.primary,
                "primary_index": self.primary_index,
                "secondary": self.secondary,
                "secondary_index": self.secondary_index,
                "suffix": self.suffix}

    def compile(self):
        components = [self.position,
                      self.primary,
                      str(self.primary_index),
                      self.secondary,
                      str(self.secondary_index),
                      self.suffix]
        return ("{sep}".format(sep=NameModel.SEP)).join(components)

    def __copy(self):
        return deepcopy(self)

    def generate_primary(self):
        return self.__generate("primary_index")

    def generate_secondary(self):
        return self.__generate("secondary_index")

    def __generate(self, key):
        new = self.__copy()
        while cmds.objExists(new.compile()):
            index = getattr(new, key)
            data = new.get_data()
            data.update({key: index + 1})
            new = NameModel(**data)
        return new.compile()

    def __match(self, pattern, value, err):
        try:
            return re.match(pattern, value).group(0)
        except (AttributeError, TypeError):
            raise NameError(err)

    def __set_position(self, val):
        err = "Invalid position: '{val}'".format(val=val)
        self.__position = str(self.__match(PATTERN_POSITION, val, err)).upper()

    def __set_primary(self, val):
        err = "Invalid primary: '{val}'".format(val=val)
        self.__primary = self.__match(PATTERN_DESCRIPTION, val, err)

    def __set_primary_index(self, val):
        err = "Invalid primary: '{val}'".format(val=val)
        self.__primary_index = int(self.__match(PATTERN_INDEX, str(val), err))

    def __set_secondary(self, val):
        err = "Invalid secondary: '{val}'".format(val=val)
        self.__secondary = self.__match(PATTERN_DESCRIPTION, val, err)

    def __set_secondary_index(self, val):
        err = "Invalid secondary: '{val}'".format(val=val)
        self.__secondary_index = int(self.__match(PATTERN_INDEX, str(val), err))

    def __set_suffix(self, val):
        err = "Invalid suffix: '{val}'".format(val=val)
        self.__suffix = self.__match(PATTERN_SUFFIX, val, err)

    def __tokenize(self):
        return (self.position, self.primary, self.primary_index,
                self.secondary, self.secondary_index)
