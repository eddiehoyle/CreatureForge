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

        self.node = libName.compile(self.position,
                                    self.descrption,
                                    self.index,
                                    self.SUFFIX)

    def __str__(self):
        return self.node

    def __repr__(self):
        return "<%s '%s'>" % (self.__class__.__name__, self.node)

    def __hash__(self):
        return hash(self.node)

    def __getitem__(self, index):
        return self.node[index]

    def __eq__(self, other):
        try:
            return self.node == other.name
        except Exception:
            return self.node == str(other)

    def __ne__(self, other):
        try:
            return self.node != other.name
        except Exception:
            return self.node == str(other)

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
