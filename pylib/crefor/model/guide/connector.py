#!/usr/bin/env python

"""
"""

import json
from copy import deepcopy
from maya import cmds
from crefor.model import Node
from crefor.model.shader import Shader
from crefor.lib import libName, libAttr

from crefor import log
logger = log.get_logger(__name__)

__all__ = ["Connector"]

class Connector(Node):

    SUFFIX = 'cnc'
    RADIUS = 0.4
    DASHED_COUNT = 3
    CLUSTER_OFFSET = 1.0

    def __init__(self, parent, child):
        super(Connector, self).__init__(*libName.decompile(str(child), 3))

        # Guides
        self.__parent = parent
        self.__child = child

        # Cluster transforms
        self.start = None
        self.end = None

        # Collection of nodes for re-init
        self.__nodes = {}

    @property
    def parent(self):
        """
        """

        return self.__parent

    @property
    def child(self):
        """
        """

        return self.__child

    @property
    def nodes(self):
        """nodes(self)
        Return important nodes from Guide class

        :returns:   Dictionary of important nodes in {"attr": "value"} format
        :rtype:     dict

        **Example**:

        >>> arm = Guide("L", "arm", 0).create()
        >>> arm.nodes
        # Result: {u'nondag': [u'L_armLocal_0_cond'], "...": "..."} # 
        """

        if self.exists():
            if not self.__nodes:
                self.__nodes = json.loads(cmds.getAttr("%s.nodes" % self.node))
            return self.__nodes
        return {}

    def __create_nodes(self):
        """
        """


        self.node = cmds.createNode("annotationShape", name=self.node)
        cmds.setAttr("%s.overrideEnabled" % self.node, True)
        cmds.setAttr("%s.overrideColor" % self.node, 18)
        cmds.setAttr("%s.displayArrow" % self.node, False)

        # Attributes for reinit
        for key in ["nodes", "geo", "nondag", "states", "shaders"]:
            cmds.addAttr(self.node, ln=key, dt='string')
            cmds.setAttr('%s.%s' % (self.node, key), k=False)

        transform = cmds.listRelatives(self.node, parent=True)[0]

        cmds.parent(self.node, self.parent.node, shape=True, relative=True)
        cmds.delete(transform)

        cmds.setAttr("%s.displayArrow" % self.node, True)
        cmds.connectAttr("%s.worldMatrix[0]" % self.child.shapes[0],
                         "%s.dagObjectMatrix[0]" % self.node,
                         force=True)

    def __update_aim_index(self):
        """
        Refresh aim index of aim condition
        """

        if self.exists():

            # Query parent joint enum items
            enums = cmds.attributeQuery("aimAt", node=self.__parent.node, listEnum=True)[0].split(':')
            enum_index = enums.index(self.__child.node)

            # Update index to reflect alias index of child
            cmds.setAttr("%s.secondTerm" % self.parent.aim_cond, enum_index)

    def __post(self):
        """
        """

        # Burn in nodes
        cmds.setAttr("%s.nodes" % self.node, json.dumps(self.__nodes), type="string")

        # Remove selection access
        cmds.setAttr("%s.overrideEnabled" % self.node, 1)
        cmds.setAttr("%s.overrideDisplayType" % self.node, 1)

    def create(self):
        """
        """

        self.__create_nodes()

        self.__post()

    def remove(self):
        """
        """

        cmds.delete(self.node)

    def reinit(self):
        """
        Reinitialise all transforms, shaders, deformers
        """

        if not self.exists():
            raise Exception('Cannot reinit \'%s\' as connector does not exist.' % self.node)

        self.__nodes = json.loads(cmds.getAttr("%s.nodes" % self.node) or "{}")

        # Get setup node:
        for key, item in self.nodes.items():
            setattr(self, key, item)

        # Refresh aim index
        self.__update_aim_index()

        return self














































