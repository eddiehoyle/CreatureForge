#!/usr/bin/env python

"""
Constraint handlers
"""

from maya import cmds


class BaseConstraintHandler(object):

    def __init__(self, constraint):

        self.__constraint = constraint

    @property
    def constraint(self):
        return self.__constraint


class AimConstraintHandler(BaseConstraintHandler):

    def aliases(self):
        return cmds.aimConstraint(self.constraint, q=True, wal=True)

HANDLERS = {"aimConstraint": AimConstraintHandler}


def get_handler(constraint):
    constraint_type = cmds.nodeType(constraint)
    return HANDLERS.get(constraint_type)
