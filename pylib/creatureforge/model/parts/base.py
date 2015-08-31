#!/usr/bin/env python

"""
"""

from creatureforge.model.base import Module
from creatureforge.model.base import ModuleModelBase

class PartModelBase(ModuleModelBase):

    SUFFIX = "prt"

class ComponentModelBase(ModuleModelBase):

    suffix = "cmp"
