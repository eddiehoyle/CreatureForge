#!/usr/bin/env python

'''
'''

from maya import cmds
from crefor.model import DAG
from crefor.lib import libShader, libName

class GuideModel(DAG):
    def __init__(self, position, description, index=0):
        super(GuideModel, self).__init__(position, description, index)