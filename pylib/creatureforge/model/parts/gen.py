#!/usr/bin/env python

"""
"""

from maya import cmds

from creatureforge.control import name
from creatureforge.model.parts._base import PartModelBase


class PartGenModel(PartModelBase):
    """
    Generic empty part with no components
    """

    SUFFIX = "prt"

    def __init__(self, position, primary, primary_index, secondary, secondary_index):
        super(PartGenModel, self).__init__(position, primary, primary_index, secondary, secondary_index)

    def _create(self):
        """Override!
        """
        pass
