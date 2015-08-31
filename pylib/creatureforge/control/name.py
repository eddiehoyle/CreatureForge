#!/usr/bin/env python

import logging

from maya import cmds

from creatureforge.model.gen.name import NameModel
from creatureforge.model.gen.name import validate

logger = logging.getLogger(__name__)

def create(position, primary, primart_index, secondary, secondary_index, suffix):
    return NameModel(position, primary, primart_index, secondary, secondary_index, suffix).compile()


@validate
def generate_primary(name):
    return NameModel(*decompile(name)).generate_primary()


@validate
def generate_secondary(name):
    return NameModel(*decompile(name)).generate_secondary()


@validate
def get_position(name):
    return NameModel(*decompile(name)).position


@validate
def get_primary(name):
    return NameModel(*decompile(name)).primary


@validate
def get_primary_index(name):
    return NameModel(*decompile(name)).primary_index


@validate
def get_secondary(name):
    return NameModel(*decompile(name)).secondary


@validate
def get_secondary_index(name):
    return NameModel(*decompile(name)).secondary_index


@validate
def suffix(name):
    return NameModel(*decompile(name)).suffix


@validate
def rename(name, **kwargs):
    data = reinit(name).get_data()
    for key in data:
        new_value = kwargs.get(key)
        if new_value is not None:
            data.update({key: new_value})
    if kwargs.get("shape"):
        shape_index = 0
        shape_name = "{suffix}Shape{index}".format(suffix=data["suffix"], index=shape_index)
        while cmds.objExists(shape_name):
            shape_index += 1
            shape_name = "{suffix}Shape{index}".format(suffix=data["suffix"], index=shape_index)
        data.update({"suffix": shape_name})
    return NameModel(**data)


@validate
def tokenize(name):
    return decompile(name)[:-1]


@validate
def decompile(name):
    return NameModel(*str(name).split(NameModel.SEP)).get_components()


@validate
def reinit(name):
    return NameModel(*decompile(str(name)))


def is_valid(name):
    try:
        return bool(decompile(name))
    except Exception as excp:
        logger.error(excp.args[0])
        return False
