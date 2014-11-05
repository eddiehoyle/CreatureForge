#!/usr/bin/env python

'''
'''

from crefor.model.guide import TransformModel

class GuideModel(TransformModel):

    suffix = 'gde'

    def __init__(self, position, description, index=0):
        super(GuideModel, self).__init__()

        self.position = position
        self.description = description
        self.index = index

        self.transform = None
        self.shape = None
        self.up = None

    def get_parent(self):
        return None

    def get_child(self):
        return None

    def __create_geometry(self):
        pass

    def __create_attribtues(self):
        pass

    def init(self):
        pass

    def create(self):
        self.__create_geometry()
        self.__create_attribtues()


