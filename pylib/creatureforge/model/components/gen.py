#!/usr/bin/env python

"""
"""

import time
import logging
from collections import OrderedDict

from maya import cmds

from creatureforge.lib import libxform
from creatureforge.lib import libattr
from creatureforge.control import name
from creatureforge.control import handle
from creatureforge.model.components._base import ComponentModelBase


logger = logging.getLogger(__name__)


class ComponentGenModel(ComponentModelBase):
    """
    """

    def __init__(self, position, primary, primary_index, secondary,
                 secondary_index):
        super(ComponentGenModel, self).__init__(position, primary,
                                                primary_index, secondary,
                                                secondary_index)

    def _create(self):
        """
        """
        pass
