#!/usr/bin/env python

"""
Guide model
"""

import json
from maya import cmds
from crefor import log
from crefor.lib import libName, libShader, libAttr
from crefor.model import Node

logger = log.get_logger(__name__)

__all__ = ["Up"]

class Up(Node):
    """
    """

    SUFFIX = "up"
    DEFAULT_SCALE = 0.2

    def __init__(self, guide):
        super(Up, self).__init__(*libName.decompile(str(guide), 3))

        self.guide = guide

        self.__shapes = {}
        self.__snapshot_nodes = {}

    @property
    def nodes(self):
        """nodes(self)
        Return important nodes from Guide class

        :returns:   Dictionary of important nodes in {"attr": "value"} format
        :rtype:     dict

        **Example**:

        >>> arm = Guide("L", "arm", 0).create()
        >>> up = Up(arm)
        >>> up.nodes
        # Result: {u'nodes': [u'L_armLocal_0_cond'], "...": "..."} # 
        """

        return json.loads(cmds.getAttr("%s.snapshotNodes" % self.node)) if self.exists() else {}

    def get_shape(self, axis):
        """
        """

        try:
            return getattr(self, axis.lower())
        except AttributeError:
            return None

    def get_position(self, local=False):
        """
        """

        return cmds.xform(self.node,
                          q=True,
                          ws=not local,
                          t=True) if self.exists() else None

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

    def set_position(self, vector3f, local=False):
        """
        """

        if self.exists():
            try:
                # cmds.setAttr("%s.translate" % self.node, *vector3f, type="float3")
                cmds.xform(self.node, ws=not local, t=vector3f)
            except Exception:
                logger.error("Failed to set translates on '%s' with args: '%s'" % (self.node, vector3f))

    def __create_nodes(self):
        """
        """

        self.node = cmds.group(name=self.node, empty=True)
        self.grp = cmds.group(self.node, name=libName.update(self.node, append="up", suffix="grp"))

        for attr in ["translate", "rotate"]:
            for axis in ["X", "Y", "Z"]:
                cmds.setAttr("%s.%s%s" % (self.grp, attr, axis), k=False)
                cmds.setAttr("%s.%s%s" % (self.grp, attr, axis), l=True)

        for attr in ["rotate", "scale"]:
            for axis in ["X", "Y", "Z"]:
                cmds.setAttr("%s.%s%s" % (self.node, attr, axis), k=False)
                cmds.setAttr("%s.%s%s" % (self.node, attr, axis), l=True)
        cmds.setAttr("%s.visibility" % self.node, k=False)
        cmds.setAttr("%s.visibility" % self.node, l=True)

        _x = cmds.sphere(name=libName.update(self.node, append="X", suffix="up"), radius=self.DEFAULT_SCALE)[0]
        _y = cmds.sphere(name=libName.update(self.node, append="Y", suffix="up"), radius=self.DEFAULT_SCALE)[0]
        _z = cmds.sphere(name=libName.update(self.node, append="Z", suffix="up"), radius=self.DEFAULT_SCALE)[0]

        self.x = cmds.listRelatives(_x, type="nurbsSurface")[0]
        self.y = cmds.listRelatives(_y, type="nurbsSurface")[0]
        self.z = cmds.listRelatives(_z, type="nurbsSurface")[0]

        cmds.parent([self.x, self.y, self.z], self.node, r=True, s=True)

        for axis in ["X", "Y", "Z"]:
            cmds.connectAttr("%s.guideScale" % self.guide.node, "%s.scale%s" % (self.grp, axis))

        # Tidy up
        cmds.parent(self.grp, self.guide.setup_node)

        cmds.delete(self.node, ch=True)
        cmds.delete([_x, _y, _z])

        self.__snapshot_nodes["x"] = self.x
        self.__snapshot_nodes["y"] = self.y
        self.__snapshot_nodes["z"] = self.z
        self.__snapshot_nodes["grp"] = self.grp

        # Add attributes
        cmds.addAttr(self.node, ln="guideScale", at="double", min=0.01, dv=1)
        cmds.setAttr("%s.guideScale" % self.node, k=False)
        cmds.setAttr("%s.guideScale" % self.node, cb=True)

        # Create scale cluster
        _cl, _scale = cmds.cluster([self.x, self.y, self.z])
        cmds.setAttr("%s.relative" % _cl, True)
        self.scale = cmds.rename(_scale, libName.update(self.node, append="upScale", suffix="clh"))
        cmds.parent(self.scale, self.node)

        for axis in ["X", "Y", "Z"]:
            cmds.connectAttr("%s.guideScale" % self.node, "%s.scale%s" % (self.scale, axis))

        # Offset node
        cmds.setAttr("%s.translateY" % self.node, 2)

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

            cmds.setAttr("%s.color" % shader, *rgb, type="float3")
            cmds.setAttr("%s.incandescence" % shader, *rgb, type="float3")
            cmds.setAttr("%s.diffuse" % shader, 0)

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

        # Lock down cluster
        cmds.setAttr("%s.visibility" % self.scale, False)
        libAttr.lock_translates(self.scale, hide=True)
        libAttr.lock_rotates(self.scale, hide=True)
        libAttr.lock_vis(self.scale, hide=True)

    def create(self):
        """
        """

        if self.exists():
            msg = "Cannot create Up model '%s', already exists with guide: '%s'" % (self.node, self.guide.node)
            logger.error(msg)
            raise RuntimeError(msg)

        self.__create_nodes()
        self.__create_shaders()

        self.__post()

        return self

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
