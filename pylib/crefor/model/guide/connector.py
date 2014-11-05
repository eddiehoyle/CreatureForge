#!/usr/bin/env python

'''
'''

from crefor.model.guide import TransformModel

class ConnecterModel(TransformModel):

    suffix = 'cnc'

    def __init__(self, parent, child):
        super(ConnectorModel, self).__init__()

        self.parent = parent
        self.child = child

        self.start = None
        self.end = None

        self.start_cl = None
        self.end_cl = None

    def get_parent(self):
        return self.parent

    def get_child(self):
        return self.child

    def __create_geometry(self):
        pass

    def __create_attribtues(self):
        pass

    def init(self):
        pass

    def create(self):
        self.__create_geometry()
        self.__create_attribtues()
