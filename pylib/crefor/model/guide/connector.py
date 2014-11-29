
#!/usr/bin/env python

'''
'''

import re
from maya import cmds
from crefor.model import Node
from crefor.lib import libName, libShader, libAttr

class Connector(Node):

    SUFFIX = 'cnc'
    RADIUS = 0.4
    DASHED_COUNT = 3
    DEFAULT_AXIS = 'X'
    CLUSTER_OFFSET = 1.0

    def __init__(self, parent, child):
        super(Connector, self).__init__(*libName._decompile(child.name)[:-1])

        self.top_node = None
        self.parent = parent
        self.child = child

        self.start = None
        self.end = None

        self.start_cl = None
        self.end_cl = None

        self.state_node = None

        self.__geometry = {}

        self.shaders = {}
        self.nodes = []

        self.axis = self.DEFAULT_AXIS

    def exists(self):
        '''Does connector exist'''
        return cmds.objExists(self.name)

    def set_scale(self, value):
        '''Scale start and end clusters'''
        if self.exists():
            cmds.setAttr('%s.scale' % self.start, *(value, value, value), type='float3')
            cmds.setAttr('%s.scale' % self.end, *(value, value, value), type='float3')

    def set_axis(self, axis='X'):
        '''
        '''

        if self.exists():

            axis = str(axis).upper()
            if axis == 'X':
                sg = self.shaders['X']['sg']
                cmds.sets(self.__get_shapes("X", "solid"), edit=True, forceElement=sg)
                cmds.sets(self.__get_shapes("X", "dashed"), edit=True, forceElement=sg)
            elif axis == 'Y':
                sg = self.shaders['Y']['sg']
                cmds.sets(self.__get_shapes("Y", "solid"), edit=True, forceElement=sg)
                cmds.sets(self.__get_shapes("Y", "dashed"), edit=True, forceElement=sg)
            elif axis == 'Z':
                sg = self.shaders['Z']['sg']
                cmds.sets(self.__get_shapes("Z", "solid"), edit=True, forceElement=sg)
                cmds.sets(self.__get_shapes("Z", "dashed"), edit=True, forceElement=sg)
            else:
                sg = self.shaders['N']['sg']
                cmds.sets(self.__get_shapes("N", "solid"), edit=True, forceElement=sg)
                cmds.sets(self.__get_shapes("N", "dashed"), edit=True, forceElement=sg)

    @property
    def transform(self):
        if cmds.objExists(self.top_node):
            return None
        #     if cmds.getAttr('%s.visibility' % self.__solid_transform):
        #         return self.__solid_transform
        #     else:
        #         return self.__dashed_transform
        else:
            return None

    def set_display(self, state='solid'):
        if self.state_node:
            if state == 'solid':
                cmds.setAttr('%s.display' % self.state_node, 0)
            elif state == 'dashed':
                cmds.setAttr('%s.display' % self.state_node, 1)

    def set_start_offset(self, value):
        if self.start and self.end:
            cmds.move(value * -1, self.start, y=True)

    def set_end_offset(self, value):
        if self.start and self.end:
            cmds.move(value, self.end, y=True)

    def set_aim_scale(self, value):
        if self.aim:
            cmds.setAttr('%s.scale' % self.aim, value, value, value, type='float3')

    def set_connector_scale(self, value):
        if self.start and self.end:
            self.set_start_scale(value)
            self.set_end_scale(value)

    def set_start_scale(self, value):
        if self.start:
            cmds.setAttr('%s.scale' % self.start, value, value, value, type='float3')

    def set_end_scale(self, value):
        if self.end:
            cmds.setAttr('%s.scale' % self.end, value, value, value, type='float3')

    def get_parent(self):
        return self.parent

    def get_child(self):
        return self.child

    def state(self):
        '''
        '''

        if self.state_node:
            state = cmds.getAttr('%s.display' % self.state_node, 0)
            if state == 0:
                return 'solid'
            elif state == 1:
                return 'dashed'
        return None

    def __create_top_node(self):
        '''
        '''

        self.top_node = cmds.group(name=self.name,
                                   empty=True)
        cmds.setAttr('%s.inheritsTransform' % self.top_node, False)
        cmds.parent(self.top_node, self.child.setup_node)

    def __get_all_transforms(self):
        transforms = []
        for axis in self.__geometry:
                solid = self.__get_transform(axis, "solid")
                dashed = self.__get_transform(axis, "dashed")
                transforms.extend([solid, dashed])
        return transforms

    def __get_all_shapes(self):
        shapes = []
        for axis in self.__geometry:
            for _type in self.__geometry[axis]:
                shapes.extend(cmds.listRelatives(self.__geometry[axis][_type],
                                                 children=True,
                                                 type="mesh") or [])
        return shapes

    def __get_transform(self, axis, state):
        return self.__geometry.get(axis, {}).get(state, None)

    def __get_shapes(self, axis, state):
        return cmds.listRelatives(self.__geometry.get(axis, {}).get(state, None),
                                  children=True,
                                  type="mesh") or []

    def __get_grp(self, axis):
        return self.__geometry.get(axis, {}).get("grp", None)

    def __get_all_grps(self):
        return [self.__get_grp(axis) for axis in ["X", "Y", "Z", "N"]]

    def __create_geometry(self):
        '''
        '''

        geometry = {}

        grpX, solidX, dashedX = self.__create_geometry_axis('X')
        grpY, solidY, dashedY = self.__create_geometry_axis('Y')
        grpZ, solidZ, dashedZ = self.__create_geometry_axis('Z')
        grpN, solidN, dashedN = self.__create_geometry_axis('N')

        geometry["X"] = dict(solid=solidX, dashed=dashedX, grp=grpX)
        geometry["Y"] = dict(solid=solidY, dashed=dashedY, grp=grpY)
        geometry["Z"] = dict(solid=solidZ, dashed=dashedZ, grp=grpZ)
        geometry["N"] = dict(solid=solidN, dashed=dashedN, grp=grpN)

        self.__geometry = geometry

    def __create_geometry_axis(self, axis):
        '''
        '''

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

        grp = cmds.group([solid, dashed], name=libName.set_suffix(libName.append_description(self.name,
                                                                                             'connector%s' % axis.upper()),
                                                                                             'grp'))

        return (grp, solid, dashed)

    def __create_deformers(self):
        '''
        Lattice and clusters
        '''

        transforms = self.__get_all_transforms()

        # Create lattice
        lattice, lattice_handle, lattice_base = cmds.lattice(transforms,
                                                             divisions=(2, 2, 2),
                                                             objectCentered=True,
                                                             ldv=(2, 2, 2),
                                                             ol=True)

        self.lattice = cmds.rename(lattice, libName.set_suffix(self.name, 'ltc'))
        self.lattice_handle = cmds.rename(lattice_handle, libName.set_suffix(self.name, 'lth'))
        self.lattice_base = cmds.rename(lattice_base, libName.set_suffix(self.name, 'ltb'))

        cmds.move(0, '%s.pt[*][*][*]' % self.lattice_handle, y=True)

        self.start_cl, self.start = cmds.cluster(['%s.pt[0:1][1][0]' % self.lattice_handle, '%s.pt[0:1][1][1]' % self.lattice_handle])
        self.end_cl, self.end = cmds.cluster(['%s.pt[0:1][0][0]' % self.lattice_handle, '%s.pt[0:1][0][1]' % self.lattice_handle])

        self.start = cmds.rename(self.start, libName.set_suffix(libName.append_description(self.name, 'start'), 'clh'))
        self.end = cmds.rename(self.end, libName.set_suffix(libName.append_description(self.name, 'end'), 'clh'))

        self.start_cl = cmds.rename('%sCluster' % self.start, libName.set_suffix(libName.append_description(self.name, 'start'), 'cls'))
        self.end_cl = cmds.rename('%sCluster' % self.end, libName.set_suffix(libName.append_description(self.name, 'end'), 'cls'))

        self.start_grp = cmds.group(self.start, name=libName.set_suffix(self.start, '%sGrp' % libName.get_suffix(self.start)))
        self.end_grp = cmds.group(self.end, name=libName.set_suffix(self.end, '%sGrp' % libName.get_suffix(self.end)))

        for clh in [self.start, self.end, self.start_grp, self.end_grp]:
            cmds.xform(clh, piv=(0, 0, 0), ws=True)
            cmds.setAttr('%s.visibility' % clh, 0)

        cmds.move(self.CLUSTER_OFFSET * -1, self.start, y=True)
        cmds.move(self.CLUSTER_OFFSET, self.end, y=True)

        cmds.setAttr('%s.visibility' % self.lattice_handle, 0)
        cmds.setAttr('%s.visibility' % self.lattice_base, 0)

        # Create aim constraints for connector
        cmds.aimConstraint(self.start_grp, self.end_grp,
                           worldUpType='scene',
                           offset=(0, 180, -90),
                           aimVector=(1, 0, 0),
                           upVector=(0, 1, 0),
                           mo=False)

        cmds.aimConstraint(self.end_grp, self.start_grp,
                           worldUpType='scene',
                           offset=(0, 0, 90),
                           aimVector=(1, 0, 0),
                           upVector=(0, 1, 0),
                           mo=False)

        cmds.pointConstraint(self.parent.joint, self.start_grp, mo=False)
        cmds.pointConstraint(self.child.joint, self.end_grp, mo=False)

        # Tidy up
        # cmds.parent(transforms, self.top_node)
        cmds.parent(self.__get_all_grps(), self.top_node)
        cmds.parent([self.lattice_handle,
                     self.lattice_base,
                     self.start_grp,
                     self.end_grp], self.top_node)

        self.nodes = [self.top_node,
                      self.lattice_handle,
                      self.lattice_base,
                      self.start,
                      self.end]

        self.nodes.extend(transforms)

    def __create_nodes(self):
        '''
        '''

        # Create visibility network
        # self.state_node = cmds.createNode('reverse', name=libName.set_suffix(libName.append_description(self.name, 'state'), 'rev'))

        # cmds.addAttr(self.state_node, ln='display', at='enum', en='dashed:solid', dv=0)
        # cmds.setAttr('%s.display' % self.state_node, k=False)
        # cmds.setAttr('%s.display' % self.state_node, cb=True)
        # cmds.connectAttr('%s.display' % self.state_node, '%s.inputX' % self.state_node)

        # for attr in ['inputX', 'inputY', 'inputZ']:
        #     cmds.setAttr('%s.%s' % (self.state_node, attr), k=False)


        aliases = cmds.aimConstraint(self.parent.constraint, q=True, wal=True)
        targets = cmds.aimConstraint(self.parent.constraint, q=True, tl=True)
        index = targets.index(self.child.aim)

        enums = cmds.attributeQuery('aimAt', node=self.parent.joint, listEnum=True)[0].split(':')
        enum_index = enums.index(self.child.aim)
        condition = cmds.createNode('condition', name=libName.set_suffix(self.name, 'cond'))
        cmds.setAttr('%s.secondTerm' % condition, enum_index)
        cmds.setAttr('%s.colorIfTrueR' % condition, 1)
        cmds.setAttr('%s.colorIfFalseR' % condition, 0)
        cmds.connectAttr('%s.aimAt' % self.parent.joint, '%s.firstTerm' % condition)
        cmds.connectAttr('%s.outColorR' % condition, '%s.%s' % (self.parent.constraint, aliases[index]))
        self.nodes.append(condition)

        # cmds.connectAttr('%s.outColorR' % condition, '%s.display' % self.state_node)
        cmds.setAttr('%s.aimAt' % self.parent.joint, len(enums)-1)


        for axis_index, axis in enumerate(["X", "Y", "Z"]):

            axis_cond = cmds.createNode("condition", name=libName.set_suffix(libName.append_description(self.name, 'axis%s' % axis), 'con'))
            cmds.connectAttr("%s.aimOrder" % self.parent.joint, "%s.firstTerm" % axis_cond)

            '''
            0, 1, 2
            needs to be
            0, 1, 2, 3, 4, 5

            pairs
            0, 1
            2, 3
            4, 5

            operation must be equals
            con 0 xy
            True 1
            False 0

            con 0 xz
            True 0
            False 1


            '''

            axis_index = (axis_index * 2)

            # Deteremine axis index
            # axis_index = axis_index if not axis_index % 2 else axis_index - 1
            print "axis", axis,axis_index
            cmds.setAttr("%s.secondTerm" % axis_cond, axis_index  + 1)
            cmds.setAttr("%s.colorIfTrueR" % axis_cond, 1)
            cmds.setAttr("%s.colorIfFalseR" % axis_cond, 0)

            other_con = cmds.createNode("condition")
            cmds.connectAttr("%s.aimOrder" % self.parent.joint, "%s.firstTerm" % other_con)
            cmds.setAttr("%s.secondTerm" % other_con, axis_index)
            cmds.setAttr("%s.colorIfTrueR" % other_con, 1)
            cmds.setAttr("%s.colorIfFalseR" % other_con, 0)
            cmds.connectAttr("%s.outColorR" % other_con, "%s.colorIfFalseR" % axis_cond)
            cmds.connectAttr("%s.aimAt" % self.parent.joint, "%s.colorIfTrueR" % other_con)

            grp = self.__get_grp(axis)
            cmds.connectAttr("%s.outColorR" % axis_cond, "%s.visibility" % grp)

            # Determine solid or dashed
            state_cond = cmds.createNode("condition", name=libName.set_suffix(libName.append_description(self.name, 'state%s' % axis), 'con'))
            cmds.connectAttr("%s.aimAt" % self.parent.joint, "%s.firstTerm" % state_cond)
            cmds.setAttr("%s.secondTerm" % state_cond, enum_index)
            cmds.setAttr("%s.colorIfTrueR" % state_cond, 1)
            cmds.setAttr("%s.colorIfFalseR" % state_cond, 0)

            state_rev = cmds.createNode("reverse", name=libName.set_suffix(libName.append_description(self.name, 'state%s' % axis), 'rev'))

            solid = self.__get_transform(axis, "solid")
            dashed = self.__get_transform(axis, "dashed")
            cmds.connectAttr("%s.outColorR" % state_cond, "%s.inputX" % state_rev)
            cmds.connectAttr("%s.outputX" % state_rev, "%s.visibility" % dashed)
            cmds.connectAttr("%s.outColorR" % state_cond, "%s.visibility" % solid)

            cmds.connectAttr("%s.aimAt" % self.parent.joint, "%s.colorIfTrueR" % axis_cond)

        # N axis
        axis = "N"
        n_cond = cmds.createNode("condition", name=libName.set_suffix(libName.append_description(self.name, 'axis%s' % axis), 'con'))
        cmds.connectAttr("%s.aimAt" % self.parent.joint, "%s.firstTerm" % n_cond)
        cmds.setAttr("%s.secondTerm" % n_cond, 0)
        cmds.setAttr("%s.colorIfTrueR" % n_cond, 1)
        cmds.setAttr("%s.colorIfFalseR" % n_cond, 0)

        grp = self.__get_grp(axis)
        cmds.connectAttr("%s.outColorR" % n_cond, "%s.visibility" % grp)

        # Determine solid or dashed
        n_state_cond = cmds.createNode("condition", name=libName.set_suffix(libName.append_description(self.name, 'state%s' % axis), 'con'))
        cmds.connectAttr("%s.aimAt" % self.parent.joint, "%s.firstTerm" % n_state_cond)
        cmds.setAttr("%s.secondTerm" % n_state_cond, 0)
        cmds.setAttr("%s.colorIfTrueR" % n_state_cond, 1)
        cmds.setAttr("%s.colorIfFalseR" % n_state_cond, 0)

        solid = self.__get_transform(axis, "solid")
        dashed = self.__get_transform(axis, "dashed")
        cmds.setAttr("%s.visibility" % solid, 0)
        cmds.setAttr("%s.visibility" % dashed, 1)

        for alias in aliases:
            if not cmds.listConnections('%s.%s' % (self.parent.constraint, alias),
                                        source=True,
                                        destination=False,
                                        plugs=True):
                cmds.setAttr('%s.%s' % (self.parent.constraint, alias), 0)

    def __create_shader(self):
        '''
        Get or create RGB or None shaders
        '''

        red, red_sg = libShader.get_or_create_shader(libName.create_name('N', 'red', 0, 'shd'), 'lambert')
        green, green_sg = libShader.get_or_create_shader(libName.create_name('N', 'green', 0, 'shd'), 'lambert')
        blue, blue_sg = libShader.get_or_create_shader(libName.create_name('N', 'blue', 0, 'shd'), 'lambert')
        none, none_sg = libShader.get_or_create_shader(libName.create_name('N', 'none', 0, 'shd'), 'lambert')

        self.shaders['X'] = dict(shader=red, sg = red_sg)
        self.shaders['Y'] = dict(shader=green, sg = green_sg)
        self.shaders['Z'] = dict(shader=blue, sg = blue_sg)
        self.shaders['N'] = dict(shader=none, sg = none_sg)

        for shader, rgb in zip([red, green, blue, none], [(1, 0, 0), (0, 1, 0), (0, 0, 1), (0.7, 0.7, 0.7)]):
            cmds.setAttr('%s.color' % shader, *rgb, type='float3')
            cmds.setAttr('%s.incandescence' % shader, *rgb, type='float3')
            cmds.setAttr('%s.diffuse' % shader, 0)

        for axis in ["X", "Y", "Z", "N"]:
            self.set_axis(axis)

    def __create_attribtues(self):
        pass

    def remove(self):

        if not self.nodes:
            return self

        cmds.delete(self.nodes)

        self.top_node = None
        self.lattice_handle = None
        self.lattice_base = None
        self.start = None
        self.end = None

        return Connector(self.parent, self.child)


    def reinit(self):
        '''
        '''

        print 'reinit'
        # _top_node = libName.set_suffix(self.name, '%sGrp' % self.SUFFIX)
        # if not cmds.ls(_top_node):
        #     return None
        if not self.exists():
            return self

        self.top_node = cmds.ls(self.name)[0]
        for axis in ["X", "Y", "Z", "N"]:
            solidX = cmds.ls(libName.set_suffix(libName.append_description(self.name, 'solid%s' % axis.upper()), 'cncGeo'))[0]
            dashedX = cmds.ls(libName.set_suffix(libName.append_description(self.name, 'dashed%s' % axis.upper()), 'cncGeo'))[0]
            self.__geometry[axis] = dict(solid=solidX, dashed=dashedX)

        self.start = cmds.ls(libName.set_suffix(libName.append_description(self.name, 'start'), 'clh'))[0]
        self.start_cl = cmds.ls(libName.set_suffix(libName.append_description(self.name, 'start'), 'cls'))[0]
        self.end = cmds.ls(libName.set_suffix(libName.append_description(self.name, 'end'), 'clh'))[0]
        self.end_cl = cmds.ls(libName.set_suffix(libName.append_description(self.name, 'end'), 'cls'))[0]
        # self.state_node = cmds.ls(libName.set_suffix(libName.append_description(self.name, 'state'), 'rev'))[0]
        self.lattice_handle = cmds.ls(libName.set_suffix(self.name, 'lth'))[0]
        self.lattice_base = cmds.ls(libName.set_suffix(self.name, 'ltb'))[0]

        self.start_grp = cmds.listRelatives(self.start, parent=True)[0]
        self.end_grp = cmds.listRelatives(self.end, parent=True)[0]

        aliases = cmds.aimConstraint(self.parent.constraint, q=True, wal=True)
        targets = cmds.aimConstraint(self.parent.constraint, q=True, tl=True)
        index = targets.index(self.child.aim)

        condition = cmds.listConnections('%s.%s' % (self.parent.constraint, aliases[index]),
                                         type='condition',
                                         source=True,
                                         destination=False)[0]

        red, red_sg = libShader.get_shader(libName.create_name('N', 'red', 0, 'shd'))
        green, green_sg = libShader.get_shader(libName.create_name('N', 'green', 0, 'shd'))
        blue, blue_sg = libShader.get_shader(libName.create_name('N', 'blue', 0, 'shd'))
        none, none_sg = libShader.get_shader(libName.create_name('N', 'none', 0, 'shd'))

        self.shaders['X'] = dict(shader=red, sg = red_sg)
        self.shaders['Y'] = dict(shader=green, sg = green_sg)
        self.shaders['Z'] = dict(shader=blue, sg = blue_sg)
        self.shaders['N'] = dict(shader=none, sg = none_sg)

        # aim_aliases = cmds.aimConstraint(self.constraint, q=True, wal=True)
        # cmds.connectAttr('%s.outColorR' % condition, '%s.%s' % (self.constraint, aim_aliases[0]))

        # enums = cmds.attributeQuery('aimAt', node=self.parent.joint, listEnum=True)[0].split(':')
        # enum_index = enums.index(self.child.aim)

        # condition = cmds.createNode('condition', name=libName.set_suffix(self.name, 'cond'))

        # condition = cmds.listConnections('%s.%s' % (self.parent.constraint, aliases[index]),
        #                                  type='condition',
        #                                  source=True,
        #                                  destination=False)[0]

        # print '-'*40
        # print 'self.top_node', self.top_node
        # print 'self.__dashed_transform', self.__dashed_transform
        # print 'self.__solid_transform', self.__solid_transform
        # print 'self.start', self.start
        # print 'self.end', self.end
        # print 'self.start_grp', self.start_grp
        # print 'self.end_grp', self.end_grp
        # print 'self.state_node', self.state_node
        # print 'self.lattice_handle', self.lattice_handle
        # print 'self.lattice_base', self.lattice_base
        # print '-'*40

        self.nodes = [self.top_node,
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
        print 'c'
        if self.exists():
            return self.reinit()

        self.__create_top_node()
        self.__create_geometry()
        self.__create_deformers()
        self.__create_nodes()
        self.__create_attribtues()
        self.__create_shader()

        self.set_start_scale(1)
        self.set_end_scale(0.1)
