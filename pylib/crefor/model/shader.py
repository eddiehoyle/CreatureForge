#!/usr/bin/env python

"""
"""

from maya import cmds

from crefor.lib import libName, libShader, libAttr
from crefor.model import Node

class Shader(Node):

    SUFFIX = "shd"

    def __init__(self, position, description, index=0, shader="lambert"):
        super(Shader, self).__init__(position, description, index)

        self.__type = shader

    @property
    def type(self):
        """
        """

        return self.__type

    @property
    def shapes(self):
        """
        """

        return cmds.sets(self.sg, q=True) if self.exists() else []

    def __create_nodes(self):
        self.node = cmds.shadingNode(self.__type, asShader=True, name=self.node)
        self.sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="%sSG" % self.node)
        cmds.connectAttr("%s.outColor" % self.node,
                         "%s.surfaceShader" % self.sg)
        return [self.node, self.sg]

    def create(self):
        """
        """

        if self.exists():
            return self.reinit()

        self.__create_nodes()

        return self

    def add(self, shapes):

        if self.exists():

            if not isinstance(shapes, list):
                shapes = [shapes]

            valid_shapes = []
            for shape in shapes:
                is_shape = cmds.objectType(shape, isAType="shape")
                is_transform = cmds.objectType(shape, isAType="transform")

                if is_transform:
                    valid_shapes.extend(cmds.listRelatives(shape, children=True, shapes=True))
                elif is_shape:
                    valid_shapes.append(shape)
                else:
                    raise TypeError("%s is not a valid shape" % shape)

            existing_shapes = cmds.sets(self.sg, q=True) or []
            valid_shapes.extend(existing_shapes)

            cmds.sets(valid_shapes, edit=True, forceElement=self.sg)

    def reinit(self):
        """
        """

        if not self.exists():
            raise Exception('Cannot reinit \'%s\' as shader does not exist.' % self.node)

        try:
            self.sg = cmds.listConnections(self.node, type="shadingEngine")[0]
        except Exception:
            raise RuntimeError("No shading groups found connected to shader: %s" % self.node)
        
        return self

    def remove(self, force=False):
        """
        """

        if self.exists():
            
            if not self.shapes or force:
                cmds.delete(self.sg)
                cmds.delete(self.node)
