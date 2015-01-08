#!/usr/bin/env python

"""
Guide model
"""

import json
from maya import cmds
from crefor import log
from crefor.lib import libName, libShader
from crefor.model import Node

logger = log.get_logger(__name__)

__all__ = ["Up"]

class Up(Node):
    """
    """

    SUFFIX = "up"
    SCALE = 0.2

    def __init__(self, guide):
        super(Up, self).__init__(*libName.decompile(str(guide), 3))

        self.__shapes = {}
        self.__snapshot_nodes = {}
        self.__snapshot_nondag = {}

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

        return json.loads(cmds.getAttr("%s.snapshotNodes" % self.node)) if self.exists() else {}

    @property
    def nondag(self):
        """nodes(self)
        Return important nodes from Guide class

        :returns:   Dictionary of important nodes in {"attr": "value"} format
        :rtype:     dict

        **Example**:

        >>> arm = Guide("L", "arm", 0).create()
        >>> arm.nodes
        # Result: {u'nondag': [u'L_armLocal_0_cond'], "...": "..."} # 
        """

        return json.loads(cmds.getAttr("%s.snapshotNondag" % self.node)) if self.exists() else {}

    def exists(self):
        """
        """

        return cmds.objExists(self.node)

    def get_shape(self, axis):
        """
        """

        return self.__shapes.get(str(axis).lower())

    def flip(self):
        """
        """

        if self.exists():
            cmds.setAttr("%s.translateX" % self.node,
                         (cmds.getAttr("%s.translateX" % self.node) * -1))

    def flop(self):
        """
        """

        if self.exists():
            cmds.setAttr("%s.translateY" % self.node,
                         (cmds.getAttr("%s.translateY" % self.node) * -1))

    def set_translates(self, vector3f):
        """
        """

        if self.exists():
            try:
                cmds.setAttr("%s.translate" % self.node, *vector3f, type="float3")
            except Exception:
                logger.error("Failed to set translates on '%s' with args: '%s'" % (self.node, vector3f))

    def __create_nodes(self):
        """
        """

        cmds.group(name=self.node, empty=True)

        _x = cmds.sphere(name=libName.update(self.node, append="X", suffix="up"))[0]
        _y = cmds.sphere(name=libName.update(self.node, append="Y", suffix="up"))[0]
        _z = cmds.sphere(name=libName.update(self.node, append="Z", suffix="up"))[0]

        self.__shapes["x"] = cmds.listRelatives(_x, type="nurbsSurface")[0]
        self.__shapes["y"] = cmds.listRelatives(_y, type="nurbsSurface")[0]
        self.__shapes["z"] = cmds.listRelatives(_z, type="nurbsSurface")[0]

        cmds.parent(self.__shapes.values(), self.node, r=True, s=True)
        cmds.setAttr("%s.translateY" % self.node, 2)

        # Scale up
        _clh = cmds.cluster(self.__shapes.values())[1]
        cmds.setAttr("%s.scale" % _clh, *(Up.SCALE, Up.SCALE, Up.SCALE), type="float3")

        # Tidy up
        cmds.delete(self.node, ch=True)
        cmds.delete([_x, _y, _z])

        self.__snapshot_nodes = self.__shapes

    def __create_shaders(self):
        """
        """

        shader_data = {"X": (1, 0, 0),
                       "Y": (0, 1, 0),
                       "Z": (0, 0, 1)}

        for axis, rgb in shader_data.items():
            shader, sg = libShader.get_or_create_shader(libName.update(self.node,
                                                        position="N",
                                                        description="color%s" % axis,
                                                        index=0,
                                                        suffix="shd"), "lambert")

            cmds.setAttr('%s.color' % shader, *rgb, type='float3')
            cmds.setAttr('%s.incandescence' % shader, *rgb, type='float3')
            cmds.setAttr('%s.diffuse' % shader, 0)

            cmds.sets(self.get_shape(axis),
                      edit=True,
                      forceElement=sg)

    def __post(self):
        """
        Post node creation
        """

        # Burn in nodes
        for key in ["snapshotNodes", "snapshotNondag"]:
            cmds.addAttr(self.node, ln=key, dt='string')
            cmds.setAttr('%s.%s' % (self.node, key), k=False)

        cmds.setAttr("%s.snapshotNodes" % self.node, json.dumps(self.__snapshot_nodes), type="string")
        cmds.setAttr("%s.snapshotNondag" % self.node, json.dumps(self.__snapshot_nondag), type="string")

    def create(self):
        """
        """

        self.__create_nodes()
        self.__create_shaders()

        self.__post()

    def reinit(self):
        """
        """

        for key, item in self.nodes.items():
            setattr(self, key, item)

        return self

    def remove(self):
        """
        """

        if self.exists():
            cmds.delete(self.node)
