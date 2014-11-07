#!/usr/bin/env python

'''
'''

# from maya import cmds
from crefor.lib import libName

class Model(object):
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

        # if cmds.objExists(self.name):
        #     raise NameError('Name already exists: %s (%s)' % (self.name,
        #                                                       cmds.nodeType(self.name)))

class DAG(Model):
    '''
    ''' 

    SUFFIX = 'dag'

    def __init__(self, position, descrption, index=0):
        super(DAG, self).__init__(position, descrption, index)

        self.shader = None
        self.sg = None

        self.transform = None
        self.shapes = []
