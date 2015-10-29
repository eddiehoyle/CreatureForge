#!/usr/bin/env python

import logging

from maya import cmds

from creatureforge.model.gen.name import NameModel
from creatureforge.model.gen.name import validate

logger = logging.getLogger(__name__)


@validate
def initialise(name):
    return NameModel(*str(name).split(NameModel.SEP))


def create(position, primary, primary_index, secondary,
           secondary_index, suffix):
    return NameModel(position, primary, primary_index, secondary,
                     secondary_index, suffix)


@validate
def generate(name, secondary=False):
    while cmds.objExists(name):
        if secondary:
            update = {"secondary_index": name.secondary_index + 1}
        else:
            update = {"primary_index": name.primary_index + 1}
        data = name.data
        data.update(update)
        name = create(**data)
    return name


@validate
def rename(name, **kwargs):
    data = initialise(name).data
    for key in data:
        new_value = kwargs.get(key)
        if new_value is not None:
            data.update({key: new_value})
    if kwargs.get("shape"):
        shape_index = 0
        shape_name = "{suffix}Shape{index}".format(
            suffix=data["suffix"], index=shape_index)
        while cmds.objExists(shape_name):
            shape_index += 1
            shape_name = "{suffix}Shape{index}".format(
                suffix=data["suffix"], index=shape_index)
        data.update({"suffix": shape_name})
    return create(**data)
