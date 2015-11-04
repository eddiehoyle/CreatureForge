#!/usr/bin/env python

"""
"""

from creatureforge.model.gen.handle import HandleModel


def create_handle(position, primary, primary_index, secondary, secondary_index,
                  **kwargs):
    """
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
