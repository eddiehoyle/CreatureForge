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