#!/usr/bin/env python

import logging

from maya import cmds

from creatureforge.model.gen.name import NameModel
from creatureforge.model.gen.name import validate

logger = logging.getLogger(__name__)


@validate
def initialise(name):
    """Initialise a name into a model object

    Args:
        name (str): A valid name

    Raises:
        InvalidNameError: If the name is unrecognised as a name model

    Returns:
        name (NameModel): Name model object
    """
    return NameModel(*str(name).split(NameModel.SEP))


def create(position, primary, primary_index, secondary,
           secondary_index, suffix):
    """Create a name model

    Args:
        position (str): Position
        primary (str): Primary description
        primary_index (str, int): Primary index
        secondary (str): Secondary description
        secondary_index (str, int): Secondary index
        suffix (str): Suffix appended to the end of the name

    Raises:
        InvalidTokenError: If an input token is invalid

    Returns:
        name (NameModel): Name model object
    """
    return NameModel(position, primary, primary_index, secondary,
                     secondary_index, suffix)


@validate
def generate(name, secondary=False):
    """Generate a name model that doesn't exist in the current Maya workspace

    Args:
        name (str): A valid name
        secondary (bool): Generate a name with unique secondary index

    Raises:
        InvalidNameError: If the name is unrecognised as a name model

    Returns:
        name (NameModel): A unique name model
    """

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
    """Create a new name model based on key word argument pairs

    Args:
        name (str): A valid name
        position (str): Position
        primary (str): Primary description
        primary_index (str, int): Primary index
        secondary (str): Secondary description
        secondary_index (str, int): Secondary index
        suffix (str): Suffix appended to the end of the name
        shape (bool): Treat this model as a shape node, append shape and
            index to suffix.

    Raises:
        InvalidNameError: If the name is unrecognised as a name model
        InvalidTokenError: If an input token is invalid

    Returns:
        name (NameModel): Name model object
    """
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
