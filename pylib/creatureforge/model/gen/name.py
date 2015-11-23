#!/usr/bin/env python

import re
import logging
from copy import deepcopy
from collections import OrderedDict

logger = logging.getLogger(__name__)

DEFAULT_SUFFIX = "grp"
PATTERN_POSITION = r"^([a-zA-Z]+)$"
PATTERN_DESCRIPTION = r"^(?!^\d+)(?!^\d+$)([a-zA-Z0-9]+)$"
PATTERN_INDEX = r"^(\d+)$"
PATTERN_SUFFIX = r"^([a-zA-Z]+)[\d+]?$"


class InvalidNameError(Exception):
    pass


class InvalidTokenError(Exception):
    pass


def validate(func):
    def wraps(*args, **kwargs):
        if not len(str(args[0]).split(NameModel.SEP)) == 6:
            err = "Invalid name: {name}".format(name=args[0])
            raise InvalidNameError(err)
        return func(*args, **kwargs)
    return wraps


def match(pattern, key, value):
    """Match a pattern with a given value.

    Args:
        pattern (str): Regex pattern
        key (str): Description of matched token
        value (str): Value to match against regex pattern

    Raises:
        NameError: If value does not match regex pattern

    Returns:
        value (str): Matched regex group
    """

    try:
        return re.match(str(pattern), str(value)).group(0)
    except (AttributeError, TypeError):
        err = "Invalid token '{0}': {1}".format(key, value)
        raise InvalidTokenError(err)


class NameModel(object):
    """
    Name container immutable data
    """

    SEP = "_"
    POSITION = "position"
    PRIMARY = "primary"
    PRIMARY_INDEX = "primary_index"
    SECONDARY = "secondary"
    SECONDARY_INDEX = "secondary_index"
    SUFFIX = "suffix"

    @staticmethod
    def fmt_position(position):
        args = (PATTERN_DESCRIPTION, NameModel.POSITION, position)
        return match(*args).upper()

    @staticmethod
    def fmt_primary(primary):
        args = (PATTERN_DESCRIPTION, NameModel.PRIMARY, primary)
        return match(*args)

    @staticmethod
    def fmt_primary_index(primary_index):
        args = (PATTERN_INDEX, NameModel.PRIMARY_INDEX, str(primary_index))
        return int(match(*args))

    @staticmethod
    def fmt_secondary(secondary):
        args = (PATTERN_DESCRIPTION, NameModel.SECONDARY, secondary)
        return match(*args)

    @staticmethod
    def fmt_secondary_index(secondary_index):
        args = (PATTERN_INDEX, NameModel.SECONDARY_INDEX, str(secondary_index))
        return int(match(*args))

    @staticmethod
    def fmt_suffix(suffix):
        args = (PATTERN_SUFFIX, NameModel.SUFFIX, suffix)
        return match(*args)

    def __init__(self, position, primary, primary_index, secondary,
                 secondary_index, suffix):

        self.__position = NameModel.fmt_position(position)
        self.__primary = NameModel.fmt_primary(primary)
        self.__primary_index = NameModel.fmt_primary_index(primary_index)
        self.__secondary = NameModel.fmt_secondary(secondary)
        self.__secondary_index = NameModel.fmt_secondary_index(secondary_index)
        self.__suffix = NameModel.fmt_suffix(suffix)
        self.__data = {}

    def __str__(self):
        return self.__compile()

    def __repr__(self):
            return "<{cls} '{name}'>".format(
                cls=self.__class__.__name__,
                name=self.__compile())

    def __compile(self):
        return "{sep}".format(sep=NameModel.SEP).join(
            map(str, self.data.values()))

    @property
    def position(self):
        return self.__position

    @property
    def primary(self):
        return self.__primary

    @property
    def primary_index(self):
        return int(self.__primary_index)

    @property
    def secondary(self):
        return self.__secondary

    @property
    def secondary_index(self):
        return int(self.__secondary_index)

    @property
    def suffix(self):
        return self.__suffix

    @property
    def tokens(self):
        return (self.position,
                self.primary,
                self.primary_index,
                self.secondary,
                self.secondary_index)

    @property
    def data(self):
        if not self.__data:
            self.__data = OrderedDict([
                (NameModel.POSITION, self.position),
                (NameModel.PRIMARY, self.primary),
                (NameModel.PRIMARY_INDEX, self.primary_index),
                (NameModel.SECONDARY, self.secondary),
                (NameModel.SECONDARY_INDEX, self.secondary_index),
                (NameModel.SUFFIX, self.suffix),
            ])
        return deepcopy(self.__data)

    # def rename(self, **kwargs):
    #     """TODO:
    #         Should this method exist here?
    #         Does it make sense to name it 'rename'?
    #     """
    #     data = self.data
    #     data.update(**kwargs)
        # return NameModel(**data)
