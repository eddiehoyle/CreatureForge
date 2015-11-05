#!/usr/bin/env python

"""
"""

from creatureforge.control import name
from creatureforge.model.gen.handle import HandleModel


def initialise(dag):
    """Initialise a control handle model if it exists

    Args:
        dag (str): Name of control handle dag node

    Returns:
        name (HandleModel): Initialised
    """

    name_model = name.initialise(str(dag))
    model = HandleModel(*name_model.tokens)

    # TODO:
    #   Type check this data, 'dag' might not be a control.
    if not model.exists:
        raise ValueError("Control handle '{0}' does not exist!".format(dag))
    return model


def create_handle(position, primary, primary_index, secondary, secondary_index,
                  **kwargs):
    """Create control handle and shapes model.

    Args:
        position (str): Position
        primary (str): Primary description
        primary_index (str, int): Primary index
        secondary (str): Secondary description
        secondary_index (str, int): Secondary index

    Return:
        model (HandleModel): Initialised control handle model.
    """

    model = HandleModel(
        position,
        primary,
        primary_index,
        secondary,
        secondary_index)
    model.set_style(kwargs.get("style", HandleModel.DEFAULT_STYLE))
    model.set_color(kwargs.get("color", HandleModel.DEFAULT_COLOR))
    model.create()
    return model
