#!/usr/bin/env python

"""
"""

import json
from copy import deepcopy
from maya import cmds
from crefor.model import Node
from crefor.lib import libName, libShader, libAttr

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

        # Cluster nodes
        self.start_cl = None
        self.end_cl = None

        # Geometry
        self.__geometry = {}
        self.__shaders = {}

        # Collection of nodes for re-init
        self.__nodes = {}
        self.__nondag = []
        self.__states = {}
        self.__geo = {}

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

        return json.loads(cmds.getAttr("%s.nondag" % self.node)) if self.exists() else {}

    @property
    def states(self):
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
            if not self.__states:
                self.__states = json.loads(cmds.getAttr("%s.states" % self.node))
            return self.__states
        return {}

    @property
    def geo(self):
        """geometry(self)
        Return geometry from Guide class

        :returns:   Dictionary of important nodes in {"attr": "value"} format
        :rtype:     dict

        **Example**:

        >>> arm = Guide("L", "arm", 0).create()
        >>> arm.nodes
        # Result: {u'nondag': [u'L_armLocal_0_cond'], "...": "..."} # 
        """

        return json.loads(cmds.getAttr("%s.geo" % self.node)) if self.exists() else {}

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

    def set_scale(self, value):
        """
        Scale start and end clusters
        """

        if self.exists():
            cmds.setAttr('%s.scale' % self.start, *(value, value, value), type='float3')
            cmds.setAttr('%s.scale' % self.end, *(value, value, value), type='float3')

    def set_start_scale(self, value):
        """
        """

        if self.start:
            cmds.setAttr('%s.scale' % self.start, value, value, value, type='float3')

    def set_end_scale(self, value):
        """
        """

        if self.end:
            cmds.setAttr('%s.scale' % self.end, value, value, value, type='float3')

    def __get_transform(self, axis, state):
        """
        Get axis and state transform
        """

        return self.__geometry.get(axis, {}).get(state, None)

    def __get_all_transforms(self):
        """
        Get all dashed and solid geometry
        """

        transforms = []
        for axis in self.__geometry:
                transforms.extend([self.__get_transform(axis, "solid"),
                                   self.__get_transform(axis, "dashed")])
        return transforms

    def __get_shapes(self, axis, state):
        """
        Get axis and state shapes
        """

        return cmds.listRelatives(self.__geometry.get(axis, {}).get(state, None),
                                  children=True,
                                  type="mesh") or []

    def __get_all_shapes(self):
        """
        Get all dashed and solid shapes
        """

        shapes = []
        for axis in self.__geometry:
            for _type in self.__geometry[axis]:
                shapes.extend(cmds.listRelatives(self.__geometry[axis][_type],
                                                 children=True,
                                                 type="mesh") or [])
        return shapes

    def __get_grp(self, axis):
        """
        Get group of axis, parent of solid and dashed geometry
        """

        return self.__geometry.get(axis, {}).get("grp", None)

    def __get_all_grps(self):
        """
        Get all groups of dashed and solid geometry
        """

        return [self.__get_grp(axis) for axis in ["X", "Y", "Z", "N"]]

    def __create_nodes(self):
        """
        Top node is a group node that is parent of all connector nodes
        """

        cmds.group(name=self.node, empty=True)
        cmds.setAttr('%s.inheritsTransform' % self.node, False)
        cmds.parent(self.node, self.__parent.setup)

        # Attributes for reinit
        for key in ["nodes", "geo", "nondag", "states"]:
            cmds.addAttr(self.node, ln=key, dt='string')
            cmds.setAttr('%s.%s' % (self.node, key), k=False)

        self.__nodes["node"] = self.node

    def __create_geometry(self):
        """
        Creat X, Y, Z and N solid and dashed geometry
        """

        for axis in ["X", "Y", "Z", "N"]:

            solid = cmds.polyCylinder(name=libName.update(self.node, suffix="cncGeo", append="solid%s" % axis.upper()),
                                      r=self.RADIUS,
                                      h=1,
                                      sx=16,
                                      sz=0,
                                      ax=(0, 1, 0),
                                      rcp=0,
                                      cuv=3,
                                      ch=0)[0]

            # Create dashed geometry
            pieces = []
            offset = (1.0/((self.DASHED_COUNT*2)+1))/2
            for index in range(0, ((self.DASHED_COUNT*2)+1), 2):
                piece = cmds.polyCylinder(r=self.RADIUS,
                                          h=(1.0/((self.DASHED_COUNT*2)+1)),
                                          sx=16,
                                          sz=0,
                                          ax=(0, 1, 0),
                                          rcp=0,
                                          cuv=3,
                                          ch=0)[0]
                pieces.append(piece)
                cmds.move(((1.0/((self.DASHED_COUNT*2)+1))*index)+offset, piece, y=True)

            dashed = cmds.polyUnite(pieces,
                                    ch=False,
                                    name=libName.update(self.node, suffix="cncGeo", append="dashed%s" % axis.upper()))[0]

            cmds.xform(dashed, cp=True)
            cmds.move(-0.5, dashed, y=True)

            # Create group
            grp = cmds.group([solid, dashed],
                             name=libName.update(self.node, suffix="grp", append="connector%s" % axis.upper()))

            # Store solid, dashed and grp
            self.__geometry[axis] = dict(solid=solid, dashed=dashed, grp=grp)

        # Burn geometry
        self.__geo = deepcopy(self.__geometry)

    def __create_deformers(self):
        """
        Create lattice and clusters
        """

        transforms = self.__get_all_transforms()

        # Create lattice
        lattice, lattice_handle, lattice_base = cmds.lattice(transforms,
                                                             divisions=(2, 2, 2),
                                                             objectCentered=True,
                                                             ldivisions=(2, 2, 2),
                                                             outsideLattice=True)

        # Rename lattice
        self.lattice = cmds.rename(lattice, libName.update(self.node, suffix='ltc'))
        self.lattice_handle = cmds.rename(lattice_handle, libName.update(self.node, suffix='lth'))
        self.lattice_base = cmds.rename(lattice_base, libName.update(self.node, suffix='ltb'))

        # Move lattice points to 0 on Y (worldspace)
        cmds.move(0, '%s.pt[*][*][*]' % self.lattice_handle, y=True)

        _, _start = cmds.cluster(['%s.pt[0:1][1][0]' % self.lattice_handle,
                                  '%s.pt[0:1][1][1]' % self.lattice_handle])
        _, _end = cmds.cluster(['%s.pt[0:1][0][0]' % self.lattice_handle,
                                '%s.pt[0:1][0][1]' % self.lattice_handle])

        self.start = cmds.rename(_start, libName.update(self.node, suffix="clh", append="start"))
        self.end = cmds.rename(_end, libName.update(self.node, suffix="clh", append="end"))

        self.start_cl = cmds.rename("%sCluster" % self.start, libName.update(self.node, suffix="cls", append="start"))
        self.end_cl = cmds.rename("%sCluster" % self.end, libName.update(self.node, suffix="cls", append="end"))

        self.start_grp = cmds.group(self.start, name=libName.update(self.node, suffix="clhGrp", append="start"))
        self.end_grp = cmds.group(self.end, name=libName.update(self.node, suffix="clhGrp", append="end"))

        # Hide visibility of deformers
        for clh in [self.start, self.end, self.start_grp, self.end_grp]:
            cmds.xform(clh, piv=(0, 0, 0), ws=True)
            cmds.setAttr("%s.visibility" % clh, 0)
        cmds.setAttr("%s.visibility" % self.lattice_handle, 0)
        cmds.setAttr("%s.visibility" % self.lattice_base, 0)

        # Apply offset transforms to clusters
        cmds.move(self.CLUSTER_OFFSET * -1, self.start, y=True)
        cmds.move(self.CLUSTER_OFFSET, self.end, y=True)

        # Aim clusters at each other
        for data in [(self.start_grp, self.end_grp, (0, 180, -90)),
                     (self.end_grp, self.start_grp, (0, 0, 90))]:
            grp_0, grp_1, offset = data
            cmds.aimConstraint(grp_0, grp_1,
                               worldUpType='scene',
                               offset=offset,
                               aimVector=(1, 0, 0),
                               upVector=(0, 1, 0),
                               maintainOffset=False)

        # Constrain parent and child joints to cluster grps
        cmds.pointConstraint(self.__parent.node, self.start_grp, mo=False)
        cmds.pointConstraint(self.__child.node, self.end_grp, mo=False)

        # Connect scale to guide
        for axis in ["X", "Y", "Z"]:
            cmds.connectAttr("%s.guideScale" % self.parent.node, "%s.scale%s" % (self.start_grp, axis))
            cmds.connectAttr("%s.guideScale" % self.child.node, "%s.scale%s" % (self.end_grp, axis))

            cmds.setAttr("%s.scale%s" % (self.end, axis), 0.1)

        # Lock all attributes
        libAttr.lock_all(self.start, hide=True)
        libAttr.lock_all(self.end, hide=True)

        # Store nodes
        self.__nodes["lattice_handle"] = self.lattice_handle
        self.__nodes["lattice_base"] = self.lattice_base
        self.__nodes["start_grp"] = self.start_grp
        self.__nodes["end_grp"] = self.end_grp

        # Parent geometry groups
        cmds.parent(self.__get_all_grps(), self.node)

        # Parent deformers
        cmds.parent([self.lattice_handle,
                     self.lattice_base,
                     self.start_grp,
                     self.end_grp], self.node)

    def __update_aim_index(self):
        """
        Refresh aim index of aim condition
        """

        if self.exists():

            # Query parent joint enum items
            enums = cmds.attributeQuery('aimAt', node=self.__parent.node, listEnum=True)[0].split(':')
            enum_index = enums.index(self.__child.aim)

            # Update index to reflect alias index of child
            cmds.setAttr("%s.secondTerm" % self.__aim_cond, enum_index)

            state_conds = json.loads(cmds.getAttr("%s.states" % self.node))
            for key, node in state_conds.items():
                cmds.setAttr("%s.secondTerm" % node, enum_index)

    def __create_visibility(self):
        """
        Create visibility nodes
        """

        # Query aliases and target list from parent aim constraint
        aliases = cmds.aimConstraint(self.__parent.constraint, q=True, wal=True)
        targets = cmds.aimConstraint(self.__parent.constraint, q=True, tl=True)
        index = targets.index(self.__child.aim)

        # Query parent joint enum items
        enums = cmds.attributeQuery('aimAt', node=self.__parent.node, listEnum=True)[0].split(':')
        enum_index = enums.index(self.__child.aim)

        # Create condition that turns on aim for child constraint if
        # enum index is set to match childs name
        self.__aim_cond = cmds.createNode('condition', name=libName.update(self.node, suffix="cond"))
        cmds.setAttr('%s.secondTerm' % self.__aim_cond, enum_index)
        cmds.setAttr('%s.colorIfTrueR' % self.__aim_cond, 1)
        cmds.setAttr('%s.colorIfFalseR' % self.__aim_cond, 0)
        cmds.connectAttr('%s.aimAt' % self.__parent.node, '%s.firstTerm' % self.__aim_cond)
        cmds.connectAttr('%s.outColorR' % self.__aim_cond, '%s.%s' % (self.__parent.constraint, aliases[index]))

        # Set enum to match child aim
        cmds.setAttr('%s.aimAt' % self.__parent.node, enum_index)

        # Store
        # self.__nondag.append(self.__aim_cond)
        self.__nodes["__aim_cond"] = self.__aim_cond

        # Loop through X, Y and Z axis to create vis network for
        # solid and dashed geometry state
        for axis_index, axis in enumerate(["X", "Y", "Z"]):

            # Axis are [XY, XZ, YX, YZ, ZX, ZY]
            axis_index = (axis_index * 2)
            grp = self.__get_grp(axis)

            # Condition that allows odd indexes to be visible
            even_cond = cmds.createNode("condition", name=libName.update(self.node, suffix="cond", append="axisEven%s" % axis))
            cmds.connectAttr("%s.aimOrient" % self.__parent.node, "%s.firstTerm" % even_cond)
            cmds.setAttr("%s.secondTerm" % even_cond, axis_index  + 1)
            cmds.setAttr("%s.colorIfTrueR" % even_cond, 1)
            cmds.setAttr("%s.colorIfFalseR" % even_cond, 0)
            cmds.connectAttr("%s.outColorR" % even_cond, "%s.visibility" % grp)

            # A secondary condition that allows odds to be visible
            odd_cond = cmds.createNode("condition", name=libName.update(self.node, suffix="cond", append="axisOdd%s" % axis))
            cmds.connectAttr("%s.aimOrient" % self.__parent.node, "%s.firstTerm" % odd_cond)
            cmds.setAttr("%s.secondTerm" % odd_cond, axis_index)
            cmds.setAttr("%s.colorIfTrueR" % odd_cond, 1)
            cmds.setAttr("%s.colorIfFalseR" % odd_cond, 0)
            cmds.connectAttr("%s.outColorR" % odd_cond, "%s.colorIfFalseR" % even_cond)

            # Allow room for defaults
            def_cond = cmds.createNode("condition", name=libName.update(self.node, suffix="cond", append="axisDef%s" % axis))
            cmds.connectAttr("%s.aimAt" % self.__parent.node, "%s.firstTerm" % def_cond)

            cmds.setAttr("%s.secondTerm" % def_cond, (len(self.__parent.DEFAULT_AIMS) - 1))
            cmds.setAttr("%s.colorIfTrueR" % def_cond, 1)
            cmds.setAttr("%s.colorIfFalseR" % def_cond, 0)
            cmds.setAttr("%s.operation" % def_cond, 2)

            cmds.connectAttr("%s.outColorR" % def_cond, "%s.colorIfTrueR" % even_cond)
            cmds.connectAttr("%s.outColorR" % def_cond, "%s.colorIfTrueR" % odd_cond)

            # A state condition that determines which geometry is display, solid or dashed
            state_cond = cmds.createNode("condition", name=libName.update(self.node, suffix="cond", append="state%s" % axis))
            cmds.connectAttr("%s.aimAt" % self.__parent.node, "%s.firstTerm" % state_cond)
            cmds.setAttr("%s.secondTerm" % state_cond, enum_index)
            cmds.setAttr("%s.colorIfTrueR" % state_cond, 1)
            cmds.setAttr("%s.colorIfFalseR" % state_cond, 0)

            # Store for reinit
            self.__states[axis] = state_cond

            # Geometry
            solid = self.__get_transform(axis, "solid")
            dashed = self.__get_transform(axis, "dashed")

            # A reverse node is needed to allow for alternate geometry visibility
            state_rev = cmds.createNode("reverse", name=libName.update(self.node, suffix="rev", append="state%s" % axis))
            cmds.connectAttr("%s.outColorR" % state_cond, "%s.inputX" % state_rev)
            cmds.connectAttr("%s.outputX" % state_rev, "%s.visibility" % dashed)
            cmds.connectAttr("%s.outColorR" % state_cond, "%s.visibility" % solid)

            self.__nondag.extend([odd_cond, even_cond, state_rev, state_cond])

        # The N axis is when world/local aim is set on parent joint aim
        # This allows for grey dashed geometry to be visible
        axis = "N"
        grp = self.__get_grp(axis)

        # N condition is True if aim is index 0
        n_cond = cmds.createNode("condition", name=libName.update(self.node, suffix="cond", append="axis%s" % axis))
        cmds.setAttr("%s.secondTerm" % n_cond, (len(self.__parent.DEFAULT_AIMS) - 1))
        cmds.setAttr("%s.colorIfTrueR" % n_cond, 1)
        cmds.setAttr("%s.colorIfFalseR" % n_cond, 0)
        cmds.connectAttr("%s.aimAt" % self.__parent.node, "%s.firstTerm" % n_cond)
        cmds.connectAttr("%s.outColorR" % n_cond, "%s.visibility" % grp)

        cmds.setAttr("%s.operation" % n_cond, 5)

        # Get geometry of N axis
        solid = self.__get_transform(axis, "solid")
        dashed = self.__get_transform(axis, "dashed")

        # Solid is False, dashed is True
        cmds.setAttr("%s.visibility" % solid, 0)
        cmds.setAttr("%s.visibility" % dashed, 1)

        self.__nondag.append(n_cond)

        # Loop through all aliases on and set non-connected attributes to be 0
        for alias in aliases:
            if not cmds.listConnections('%s.%s' % (self.__parent.constraint, alias),
                                        source=True,
                                        destination=False,
                                        plugs=True):
                cmds.setAttr('%s.%s' % (self.__parent.constraint, alias), 0)

    def __create_shader(self):
        """
        Get or create X(R), Y(G), Z(B) or N(Grey) shaders
        """

        shader_data = {"X": (1, 0, 0),
                       "Y": (0, 1, 0),
                       "Z": (0, 0, 1),
                       "N": (0.7, 0.7, 0.7)}

        for axis, rgb in shader_data.items():
            shader, sg = libShader.get_or_create_shader(libName.update(self.node,
                                                        position="N",
                                                        description="color%s" % axis,
                                                        index=0,
                                                        suffix="shd"), "lambert")

            cmds.setAttr('%s.color' % shader, *rgb, type='float3')
            cmds.setAttr('%s.incandescence' % shader, *rgb, type='float3')
            cmds.setAttr('%s.diffuse' % shader, 0)

            self.__shaders[axis] = dict(shader=shader, sg=sg)

            cmds.sets(self.__get_shapes(axis, "solid"), edit=True, forceElement=sg)
            cmds.sets(self.__get_shapes(axis, "dashed"), edit=True, forceElement=sg)

    def __create_attribtues(self):
        """
        """

    def __post(self):
        """
        """

        # Burn in nodes
        cmds.setAttr("%s.nodes" % self.node, json.dumps(self.__nodes), type="string")
        cmds.setAttr("%s.states" % self.node, json.dumps(self.__states), type="string")
        cmds.setAttr("%s.nondag" % self.node, json.dumps(self.__nondag), type="string")
        cmds.setAttr("%s.geo" % self.node, json.dumps(self.__geo), type="string")

        # Remove selection access
        cmds.setAttr("%s.overrideEnabled" % self.node, 1)
        cmds.setAttr("%s.overrideDisplayType" % self.node, 2)

    def reinit(self):
        """
        Reinitialise all transforms, shaders, deformers
        """

        if not self.exists():
            raise Exception('Cannot reinit \'%s\' as connector does not exist.' % self.node)

        self.__nodes = json.loads(cmds.getAttr("%s.nodes" % self.node))
        self.__nondag = json.loads(cmds.getAttr("%s.nondag" % self.node))
        self.__states = json.loads(cmds.getAttr("%s.states" % self.node))
        self.__geo = json.loads(cmds.getAttr("%s.geo" % self.node))

        # Unique attribute
        self.__aim_cond = self.nodes.pop("__aim_cond")

        # Get setup node:
        for key, item in self.nodes.items():
            setattr(self, key, item)

        # Refresh aim index
        self.__update_aim_index()

        return self

    def create(self):
        """
        Create a guide
        """

        if self.exists():
            return self.reinit()

        self.__create_nodes()
        self.__create_geometry()
        self.__create_deformers()
        self.__create_visibility()
        self.__create_shader()
        self.__post()

        return self

    def remove(self):
        """
        """

        # geo = []
        # for axis in self.geo:
        #     geo.extend(self.geo[axis].values())

        cmds.delete(self.nondag)
        cmds.delete(self.node)
