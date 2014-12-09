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

        self.name = libName.create_name(self.position,
                                        self.descrption,
                                        self.index,
                                        self.SUFFIX)

    def _decompile(self):
        """_decompile(self)

        Decompile name into components.

        :returns:   List of name componenets
        :rtype:     list

        **Example**:

        >>> guide = Guide("C", "spine", 0).create()
        >>> guide._decompile()
        # Result: ["C", "spine", 0, "gde"] #
        """

        return libName._decompile(self.name)

    def __str__(self):
        return self.name

    def __repr__(self):
        # return "%s(position=%s, descrption=%s, index=%s)" % (self.__class__.__name__,
        #                                                      self.position,
        #                                                      self.descrption,
        #                                                      self.index)
        # return "%s(%s)" % (self.__class__.__name__, self.name)
        return "<Guide '%s'>" % self.name

    def __getitem__(self, index):
        return self.name[index]

    def __eq__(self, other):
        try:
            return self.name == other.name
        except Exception:
            return False

    def __ne__(self, other):
        try:
            return self.name != other.name
        except Exception:
            return False

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
