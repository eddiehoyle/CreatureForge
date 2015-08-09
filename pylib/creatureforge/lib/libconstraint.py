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

class OrientConstraintHandler(BaseConstraintHandler):

    @property
    def aliases(self):
        return cmds.orientConstraint(self.constraint, q=True, wal=True)

    @property
    def targets(self):
        return cmds.orientConstraint(self.constraint, q=True, tl=True)


class AimConstraintHandler(BaseConstraintHandler):

    @property
    def targets(self):
        return cmds.aimConstraint(self.constraint, q=True, tl=True)

    @property
    def aliases(self):
        return cmds.aimConstraint(self.constraint, q=True, wal=True)

HANDLERS = {"aimConstraint": AimConstraintHandler,
            "orientConstraint": OrientConstraintHandler}


def get_handler(constraint):
    constraint_type = cmds.nodeType(constraint)
    handlder = HANDLERS.get(constraint_type)
    return handlder(constraint)
