
#!/usr/bin/env python

'''
'''

from maya import cmds
from crefor.model import Node
from crefor.lib import libName, libShader, libAttr

class Connector(Node):

    SUFFIX = 'cnc'
    RADIUS = 0.4
    DASHED_COUNT = 3
    CLUSTER_OFFSET = 1.0

    def __init__(self, parent, child):
        super(Connector, self).__init__(*libName._decompile(str(child))[:-1])

        # Guides
        self.__parent = parent
        self.__child = child

        # Top grp
        self.top_node = None

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
        self.__nodes = []

    @property
    def parent(self):
        return self.__parent

    @property
    def child(self):
        return self.__child

    def exists(self):
        '''Does connector exist'''
        return cmds.objExists(self.name)

    def set_scale(self, value):
        '''Scale start and end clusters'''
        if self.exists():
            cmds.setAttr('%s.scale' % self.start, *(value, value, value), type='float3')
            cmds.setAttr('%s.scale' % self.end, *(value, value, value), type='float3')

    def set_start_scale(self, value):
        if self.start:
            cmds.setAttr('%s.scale' % self.start, value, value, value, type='float3')

    def set_end_scale(self, value):
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

    def __create_top_node(self):
        """
        Top node is a group node that is parent of all connector nodes
        """

        self.top_node = cmds.group(name=self.name,
                                   empty=True)
        cmds.setAttr('%s.inheritsTransform' % self.top_node, False)
        cmds.parent(self.top_node, self.__parent.setup_node)
        self.__nodes.append(self.top_node)

    def __create_geometry(self):
        """
        Creat X, Y, Z and N solid and dashed geometry
        """

        for axis in ["X", "Y", "Z", "N"]:

            # Create solid geometry
            solid = cmds.polyCylinder(name=libName.set_suffix(libName.append_description(self.name,
                                                                                                     'solid%s' % axis.upper()),
                                                                                                     'cncGeo'),
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
                                    name=libName.set_suffix(libName.append_description(self.name,
                                                                                       'dashed%s' % axis.upper()),
                                                                                       'cncGeo'))[0]

            cmds.xform(dashed, cp=True)
            cmds.move(-0.5, dashed, y=True)

            # Create group
            grp = cmds.group([solid, dashed], name=libName.set_suffix(libName.append_description(self.name,
                                                                                                 'connector%s' % axis.upper()),
                                                                                                 'grp'))

            # Store solid, dashed and grp
            self.__geometry[axis] = dict(solid=solid, dashed=dashed, grp=grp)

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
        self.lattice = cmds.rename(lattice, libName.set_suffix(self.name, 'ltc'))
        self.lattice_handle = cmds.rename(lattice_handle, libName.set_suffix(self.name, 'lth'))
        self.lattice_base = cmds.rename(lattice_base, libName.set_suffix(self.name, 'ltb'))

        # Move lattice points to 0 on Y (worldspace)
        cmds.move(0, '%s.pt[*][*][*]' % self.lattice_handle, y=True)


        _, _start = cmds.cluster(['%s.pt[0:1][1][0]' % self.lattice_handle,
                                  '%s.pt[0:1][1][1]' % self.lattice_handle])
        _, _end = cmds.cluster(['%s.pt[0:1][0][0]' % self.lattice_handle,
                                '%s.pt[0:1][0][1]' % self.lattice_handle])

        self.start = cmds.rename(_start,
                                 libName.set_suffix(libName.append_description(self.name, 'start'),
                                 'clh'))
        self.end = cmds.rename(_end,
                               libName.set_suffix(libName.append_description(self.name, 'end'),
                               'clh'))

        self.start_cl = cmds.rename('%sCluster' % self.start,
                                    libName.set_suffix(libName.append_description(self.name, 'start'),
                                    'cls'))
        self.end_cl = cmds.rename('%sCluster' % self.end,
                                  libName.set_suffix(libName.append_description(self.name, 'end'),
                                  'cls'))

        self.start_grp = cmds.group(self.start,
                                    name=libName.set_suffix(self.start,
                                                            '%sGrp' % libName.get_suffix(self.start)))
        self.end_grp = cmds.group(self.end,
                                  name=libName.set_suffix(self.end,
                                                          '%sGrp' % libName.get_suffix(self.end)))

        # Hide visibility of deformers
        for clh in [self.start, self.end, self.start_grp, self.end_grp]:
            cmds.xform(clh, piv=(0, 0, 0), ws=True)
            cmds.setAttr('%s.visibility' % clh, 0)
        cmds.setAttr('%s.visibility' % self.lattice_handle, 0)
        cmds.setAttr('%s.visibility' % self.lattice_base, 0)

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
        cmds.pointConstraint(self.__parent.joint, self.start_grp, mo=False)
        cmds.pointConstraint(self.__child.joint, self.end_grp, mo=False)

        # Parent geometry groups
        cmds.parent(self.__get_all_grps(), self.top_node)

        # Parent deformers
        cmds.parent([self.lattice_handle,
                     self.lattice_base,
                     self.start_grp,
                     self.end_grp], self.top_node)

        # # Define nodes
        # self.__nodes = [self.top_node,
        #               self.lattice_handle,
        #               self.lattice_base,
        #               self.start,
        #               self.end]

        # self.__nodes.extend(transforms)

    def __create_visibilty_network(self):
        """
        Create visibility nodes
        """

        # Query aliases and target list from parent aim constraint
        aliases = cmds.aimConstraint(self.__parent.constraint, q=True, wal=True)
        targets = cmds.aimConstraint(self.__parent.constraint, q=True, tl=True)
        index = targets.index(self.__child.aim)

        # Query parent joint enum items
        enums = cmds.attributeQuery('aimAt', node=self.__parent.joint, listEnum=True)[0].split(':')
        enum_index = enums.index(self.__child.aim)

        # Create condition that turns on aim for child constraint if
        # enum index is set to match childs name
        aim_cond = cmds.createNode('condition', name=libName.set_suffix(self.name, 'cond'))
        cmds.setAttr('%s.secondTerm' % aim_cond, enum_index)
        cmds.setAttr('%s.colorIfTrueR' % aim_cond, 1)
        cmds.setAttr('%s.colorIfFalseR' % aim_cond, 0)
        cmds.connectAttr('%s.aimAt' % self.__parent.joint, '%s.firstTerm' % aim_cond)
        cmds.connectAttr('%s.outColorR' % aim_cond, '%s.%s' % (self.__parent.constraint, aliases[index]))

        # Set enum to match child aim
        cmds.setAttr('%s.aimAt' % self.__parent.joint, enum_index)

        # Store
        self.__nodes.append(aim_cond)

        # Loop through X, Y and Z axis to create vis network for
        # solid and dashed geometry state
        for axis_index, axis in enumerate(["X", "Y", "Z"]):

            # Axis are [XY, XZ, YX, YZ, ZX, ZY]
            axis_index = (axis_index * 2)
            grp = self.__get_grp(axis)

            # Condition that allows odd indexes to be visible
            even_cond = cmds.createNode("condition", name=libName.set_suffix(libName.append_description(self.name, 'axisEven%s' % axis), 'con'))
            cmds.connectAttr("%s.aimOrder" % self.__parent.joint, "%s.firstTerm" % even_cond)
            cmds.setAttr("%s.secondTerm" % even_cond, axis_index  + 1)
            cmds.setAttr("%s.colorIfTrueR" % even_cond, 1)
            cmds.setAttr("%s.colorIfFalseR" % even_cond, 0)
            cmds.connectAttr("%s.outColorR" % even_cond, "%s.visibility" % grp)
            cmds.connectAttr("%s.aimAt" % self.__parent.joint, "%s.colorIfTrueR" % even_cond)

            # A secondary condition that allows odds to be visible
            odd_cond = cmds.createNode("condition", name=libName.set_suffix(libName.append_description(self.name, 'axisOdd%s' % axis), 'con'))
            cmds.connectAttr("%s.aimOrder" % self.__parent.joint, "%s.firstTerm" % odd_cond)
            cmds.setAttr("%s.secondTerm" % odd_cond, axis_index)
            cmds.setAttr("%s.colorIfTrueR" % odd_cond, 1)
            cmds.setAttr("%s.colorIfFalseR" % odd_cond, 0)
            cmds.connectAttr("%s.outColorR" % odd_cond, "%s.colorIfFalseR" % even_cond)
            cmds.connectAttr("%s.aimAt" % self.__parent.joint, "%s.colorIfTrueR" % odd_cond)

            # A state condition that determines which geometry is display, solid or dashed
            state_cond = cmds.createNode("condition", name=libName.set_suffix(libName.append_description(self.name, 'state%s' % axis), 'con'))
            cmds.connectAttr("%s.aimAt" % self.__parent.joint, "%s.firstTerm" % state_cond)
            cmds.setAttr("%s.secondTerm" % state_cond, enum_index)
            cmds.setAttr("%s.colorIfTrueR" % state_cond, 1)
            cmds.setAttr("%s.colorIfFalseR" % state_cond, 0)

            # Geometry
            solid = self.__get_transform(axis, "solid")
            dashed = self.__get_transform(axis, "dashed")

            # A reverse node is needed to allow for alternate geometry visibility
            state_rev = cmds.createNode("reverse", name=libName.set_suffix(libName.append_description(self.name, 'state%s' % axis), 'rev'))
            cmds.connectAttr("%s.outColorR" % state_cond, "%s.inputX" % state_rev)
            cmds.connectAttr("%s.outputX" % state_rev, "%s.visibility" % dashed)
            cmds.connectAttr("%s.outColorR" % state_cond, "%s.visibility" % solid)

            self.__nodes.extend([odd_cond, even_cond, state_rev, state_cond])

        # The N axis is when world/local aim is set on parent joint aim
        # This allows for grey dashed geometry to be visible
        axis = "N"
        grp = self.__get_grp(axis)

        # N condition is True if aim is index 0
        n_cond = cmds.createNode("condition", name=libName.set_suffix(libName.append_description(self.name, 'axis%s' % axis), 'con'))
        cmds.setAttr("%s.secondTerm" % n_cond, 0)
        cmds.setAttr("%s.colorIfTrueR" % n_cond, 1)
        cmds.setAttr("%s.colorIfFalseR" % n_cond, 0)
        cmds.connectAttr("%s.aimAt" % self.__parent.joint, "%s.firstTerm" % n_cond)
        cmds.connectAttr("%s.outColorR" % n_cond, "%s.visibility" % grp)

        # Get geometry of N axis
        solid = self.__get_transform(axis, "solid")
        dashed = self.__get_transform(axis, "dashed")

        # Solid is False, dashed is True
        cmds.setAttr("%s.visibility" % solid, 0)
        cmds.setAttr("%s.visibility" % dashed, 1)

        self.__nodes.append(n_cond)

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
            shader, sg = libShader.get_or_create_shader(libName.create_name('N', "color%s" % axis, 0, 'shd'), "lambert")

            cmds.setAttr('%s.color' % shader, *rgb, type='float3')
            cmds.setAttr('%s.incandescence' % shader, *rgb, type='float3')
            cmds.setAttr('%s.diffuse' % shader, 0)

            self.__shaders[axis] = dict(shader=shader, sg=sg)

            cmds.sets(self.__get_shapes(axis, "solid"), edit=True, forceElement=sg)
            cmds.sets(self.__get_shapes(axis, "dashed"), edit=True, forceElement=sg)

    def __create_attribtues(self):
        pass

    def _remove(self):
        """
        """

        print 'in connector', self.name, 'nodes', self.__nodes

        if not self.__nodes:
            return self

        cmds.delete(self.__nodes)

        
        self.__nodes = []
        self.__geometry = {}

        print 'in connector', self.name, 'after', self.__nodes

        return Connector(self.__parent, self.__child)


    def reinit(self):
        """
        Reinitialise all transforms, shaders, deformers
        """

        if not self.exists():
            return self

        # Top node
        self.top_node = cmds.ls(self.name)[0]

        # Axis related nodes
        axis_nodes = []
        for axis in ["X", "Y", "Z"]:

            # Geometry and groups
            solid = cmds.ls(libName.set_suffix(libName.append_description(self.name, 'solid%s' % axis.upper()), 'cncGeo'))[0]
            dashed = cmds.ls(libName.set_suffix(libName.append_description(self.name, 'dashed%s' % axis.upper()), 'cncGeo'))[0]
            grp  = cmds.ls(libName.set_suffix(libName.append_description(self.name, 'connector%s' % axis.upper()), 'grp'))[0]
            self.__geometry[axis] = dict(solid=solid, dashed=dashed, grp=grp)

            # Shaders
            shader, sg = libShader.get_shader(libName.create_name('N', "color%s" % axis, 0, 'shd'))
            self.__shaders[axis] = dict(shader=shader, sg=sg)

            # Conditions and other network nodes
            aim_cond = cmds.ls(libName.set_suffix(self.name, 'cond'))[0]
            even_cond = cmds.createNode("condition", name=libName.set_suffix(libName.append_description(self.name, 'axisEven%s' % axis), 'con'))
            odd_cond = cmds.createNode("condition", name=libName.set_suffix(libName.append_description(self.name, 'axisOdd%s' % axis), 'con'))
            state_cond = cmds.ls(libName.set_suffix(libName.append_description(self.name, 'state%s' % axis), 'con'))[0]
            state_rev = cmds.ls(libName.set_suffix(libName.append_description(self.name, 'state%s' % axis), 'rev'))[0]
            axis_nodes.extend([aim_cond, even_cond, odd_cond, state_cond, state_rev])

        axis = "N"
        solid = cmds.ls(libName.set_suffix(libName.append_description(self.name, 'solid%s' % axis.upper()), 'cncGeo'))[0]
        dashed = cmds.ls(libName.set_suffix(libName.append_description(self.name, 'dashed%s' % axis.upper()), 'cncGeo'))[0]
        grp  = cmds.ls(libName.set_suffix(libName.append_description(self.name, 'connector%s' % axis.upper()), 'grp'))[0]
        self.__geometry[axis] = dict(solid=solid, dashed=dashed, grp=grp)

        n_cond = cmds.ls(libName.set_suffix(libName.append_description(self.name, 'axis%s' % axis), 'con'))[0]
        axis_nodes.append(n_cond)

        # Clusters
        self.start = cmds.ls(libName.set_suffix(libName.append_description(self.name, 'start'), 'clh'))[0]
        self.start_cl = cmds.ls(libName.set_suffix(libName.append_description(self.name, 'start'), 'cls'))[0]
        self.end = cmds.ls(libName.set_suffix(libName.append_description(self.name, 'end'), 'clh'))[0]
        self.end_cl = cmds.ls(libName.set_suffix(libName.append_description(self.name, 'end'), 'cls'))[0]
        self.start_grp = cmds.listRelatives(self.start, parent=True)[0]
        self.end_grp = cmds.listRelatives(self.end, parent=True)[0]

        # Lattices
        self.lattice_handle = cmds.ls(libName.set_suffix(self.name, 'lth'))[0]
        self.lattice_base = cmds.ls(libName.set_suffix(self.name, 'ltb'))[0]

        aliases = cmds.aimConstraint(self.__parent.constraint, q=True, wal=True)
        targets = cmds.aimConstraint(self.__parent.constraint, q=True, tl=True)
        index = targets.index(self.__child.aim)

        condition = cmds.listConnections('%s.%s' % (self.__parent.constraint, aliases[index]),
                                         type='condition',
                                         source=True,
                                         destination=False)[0]


        # Non-dag nodes
        self.__nodes.extend(axis_nodes)

        # Geometry
        geometry = self.__get_all_transforms()
        self.__nodes.extend(geometry)

        # Groups
        grps = self.__get_all_grps()
        self.__nodes.extend(grps)

        # Other
        self.__nodes = [self.top_node,
                        self.lattice_handle,
                        self.lattice_base,
                        self.start,
                        self.end,
                        self.start_grp,
                        self.end_grp,
                        condition]

        return self

    def create(self):
        '''
        '''

        if self.exists():
            return self.reinit()

        self.__create_top_node()
        self.__create_geometry()
        self.__create_deformers()
        self.__create_visibilty_network()
        self.__create_attribtues()
        self.__create_shader()

        self.set_start_scale(1)
        self.set_end_scale(0.1)
