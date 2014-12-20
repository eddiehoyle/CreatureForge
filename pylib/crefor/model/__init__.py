#!/usr/bin/env python

'''
'''

# from maya import cmds
from crefor.lib import libName

class Node(object):
    '''
    Base node
    '''

    SUFFIX = 'nde'

    def __init__(self, position, descrption, index=0):
        
        self.position = position
        self.descrption = descrption
        self.index = index

        self.name = libName.compile(self.position,
                                    self.descrption,
                                    self.index,
                                    self.SUFFIX)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<Guide '%s'>" % self.name

    def __hash__(self):
        return hash(self.name)

    def __getitem__(self, index):
        return self.name[index]

    def __eq__(self, other):
        try:
            return self.name == other.name
        except Exception:
            return self.name == str(other)

    def __ne__(self, other):
        try:
            return self.name != other.name
        except Exception:
            return self.name == str(other)

    def __lt__(self, other):
        try:
            return self.index < other.index
        except Exception:
            return False

    def __gt__(self, other):
        try:
            return self.index > other.index
        except Exception:
            return False

    def __le__(self, other):
        try:
            return self.index <= other.index
        except Exception:
            return False

    def __ge__(self, other):
        try:
            return self.index >= other.index
        except Exception:
            return False
