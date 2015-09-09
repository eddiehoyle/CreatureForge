#!/usr/bin/env python

"""
"""

import json
from collections import OrderedDict
from copy import deepcopy

from creatureforge.lib import libattr
from creatureforge.model.base import Module
from creatureforge.model.base import ModuleModelBase

from maya import cmds


class BuildBase(ModuleModelBase):

    SUFFIX = "rig"

    def __init__(self, *args, **kwargs):
        super(BuildBase, self).__init__(*args, **kwargs)
