#!/usr/bin/env python

"""
"""

from creatureforge.model.gen.name import InvalidNameError

class InvalidNameError(Exception):
    pass

class DuplicateNameError(Exception):
    pass

class InvalidGuideError(Exception):
    pass

class GuideDoesNotExistError(Exception):
    pass

class GuideHierarchyError(Exception):
    pass