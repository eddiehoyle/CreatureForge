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
    DASHED_COUNT = 5
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

        self.__dashed_transform = None
        self.__dashed_shapes = []
        self.__solid_transform = None
        self.__solid_shapes = []

        self.state_node = None

        self.shaders = {}
        self.nodes = []

        self.axis = self.DEFAULT_AXIS

    def set_scale(self, value):
        if self.start and self.end:
            cmds.setAttr('%s.scale' % self.start, *(value, value, value), type='float3')
            cmds.setAttr('%s.scale' % self.end, *(value, value, value), type='float3')

    def set_axis(self, axis='X'):
        '''
        '''

        if self.transform:
            if isinstance(axis, basestring):
                axis = axis.upper()

            if axis == 'X':
                sg = self.shaders['X']['sg']
            elif axis == 'Y':
                sg = self.shaders['Y']['sg']
            elif axis == 'Z':
                sg = self.shaders['Z']['sg']
            else:
                sg = self.shaders['N']['sg']

            # Add to geometry
            cmds.sets(self.__dashed_shapes, edit=True, forceElement=sg)
            cmds.sets(self.__solid_shapes, edit=True, forceElement=sg)

    @property
    def transform(self):
        if cmds.objExists(self.top_node):
            if cmds.getAttr('%s.visibility' % self.__solid_transform):
                return self.__solid_transform
            else:
                return self.__dashed_transform
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

        self.top_node = cmds.group(name=libName.set_suffix(self.name,
                                                           '%sGrp' % self.SUFFIX),
                                                           empty=True)
        cmds.setAttr('%s.inheritsTransform' % self.top_node, False)
        cmds.parent(self.top_node, self.child.setup_node)

    def __create_geometry(self):
        '''
        '''

        # Create solid geometry
        self.__solid_transform = cmds.polyCylinder(name=libName.append_description(self.name, 'solid'),
                                                   r=self.RADIUS,
                                                   h=1,
                                                   sx=16,
                                                   sz=0,
                                                   ax=(0, 1, 0),
                                                   rcp=0,
                                                   cuv=3,
                                                   ch=0)[0]
        self.__solid_shapes = cmds.listRelatives(self.__solid_transform, type='mesh', children=True)

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

        self.__dashed_transform = cmds.polyUnite(pieces, ch=False, name=libName.append_description(self.name, 'dashed'))[0]
        self.__dashed_shapes = cmds.listRelatives(self.__dashed_transform, type='mesh', children=True)

        cmds.xform(self.__dashed_transform, cp=True)
        cmds.move(-0.5, self.__dashed_transform, y=True)

        # Tidy up
        


    def __create_deformers(self):
        '''
        Lattice and clusters
        '''

        # Create lattice
        lattice, lattice_handle, lattice_base = cmds.lattice([self.__solid_transform, self.__dashed_transform],
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
        cmds.parent([self.__dashed_transform,
                     self.__solid_transform,
                     self.lattice_handle,
                     self.lattice_base,
                     self.start_grp,
                     self.end_grp], self.top_node)

        self.nodes = [self.top_node,
                      self.__dashed_transform,
                      self.__solid_transform,
                      self.lattice_handle,
                      self.lattice_base,
                      self.start,
                      self.end,
                      self.state_node]

        

    def __create_nodes(self):
        '''
        '''

        # Create visibility network
        self.state_node = cmds.createNode('reverse', name=libName.set_suffix(libName.append_description(self.name, 'state'), 'rev'))

        cmds.addAttr(self.state_node, ln='display', at='enum', en='dashed:solid', dv=0)
        cmds.setAttr('%s.display' % self.state_node, k=False)
        cmds.setAttr('%s.display' % self.state_node, cb=True)
        cmds.connectAttr('%s.display' % self.state_node, '%s.inputX' % self.state_node)

        for attr in ['inputX', 'inputY', 'inputZ']:
            cmds.setAttr('%s.%s' % (self.state_node, attr), k=False)

        cmds.connectAttr('%s.display' % self.state_node, '%s.visibility' % self.__solid_transform)
        cmds.connectAttr('%s.outputX' % self.state_node, '%s.visibility' % self.__dashed_transform)

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

        cmds.connectAttr('%s.outColorR' % condition, '%s.display' % self.state_node)
        cmds.setAttr('%s.aimAt' % self.parent.joint, len(enums)-1)

    def __create_shader(self):
        '''
        Get or create RGB or None shaders
        '''

        red, red_sg = libShader.get_or_create_shader(libName.create_name('C', 'red', 0, 'shd'), 'lambert')
        green, green_sg = libShader.get_or_create_shader(libName.create_name('C', 'green', 0, 'shd'), 'lambert')
        blue, blue_sg = libShader.get_or_create_shader(libName.create_name('C', 'blue', 0, 'shd'), 'lambert')
        none, none_sg = libShader.get_or_create_shader(libName.create_name('C', 'none', 0, 'shd'), 'lambert')

        self.shaders['X'] = dict(shader=red, sg = red_sg)
        self.shaders['Y'] = dict(shader=green, sg = green_sg)
        self.shaders['Z'] = dict(shader=blue, sg = blue_sg)
        self.shaders['N'] = dict(shader=none, sg = none_sg)

        for shader, rgb in zip([red, green, blue, none], [(1, 0, 0), (0, 1, 0), (0, 0, 1), (0.7, 0.7, 0.7)]):
            cmds.setAttr('%s.color' % shader, *rgb, type='float3')
            cmds.setAttr('%s.incandescence' % shader, *rgb, type='float3')
            cmds.setAttr('%s.diffuse' % shader, 0)

        self.set_axis(self.DEFAULT_AXIS)

    def __create_attribtues(self):
        pass

    def exists(self):
        '''
        '''

        return cmds.objExists(self.top_node)

    def remove(self):

        if not self.nodes:
            return self

        cmds.delete(self.nodes)

        self.top_node = None
        self.__dashed_transform = None
        self.__solid_transform = None
        self.lattice_handle = None
        self.lattice_base = None
        self.start = None
        self.end = None
        self.state_node = None

        return Connector(self.parent, self.child)


    def reinit(self):
        '''
        '''

        _top_node = libName.set_suffix(self.name, '%sGrp' % self.SUFFIX)
        if not cmds.ls(_top_node):
            return None

        self.top_node = cmds.ls(libName.set_suffix(self.name, '%sGrp' % self.SUFFIX))[0]
        self.__dashed_transform = cmds.ls(libName.append_description(self.name, 'dashed'))[0]
        self.__solid_transform = cmds.ls(libName.append_description(self.name, 'solid'))[0]
        self.start = cmds.ls(libName.set_suffix(libName.append_description(self.name, 'start'), 'clh'))[0]
        self.start_cl = cmds.ls(libName.set_suffix(libName.append_description(self.name, 'start'), 'cls'))[0]
        self.end = cmds.ls(libName.set_suffix(libName.append_description(self.name, 'end'), 'clh'))[0]
        self.end_cl = cmds.ls(libName.set_suffix(libName.append_description(self.name, 'end'), 'cls'))[0]
        self.state_node = cmds.ls(libName.set_suffix(libName.append_description(self.name, 'state'), 'rev'))[0]
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
                      self.__dashed_transform,
                      self.__solid_transform,
                      self.lattice_handle,
                      self.lattice_base,
                      self.start,
                      self.end,
                      self.start_grp,
                      self.end_grp,
                      self.state_node,
                      condition]

        return self

    def create(self):
        '''
        '''

        _top_node = libName.set_suffix(self.name, '%sGrp' % self.SUFFIX)
        if cmds.ls(_top_node):
            return self.reinit()

        self.__create_top_node()
        self.__create_geometry()
        self.__create_deformers()
        self.__create_nodes()
        self.__create_attribtues()
        self.__create_shader()

        self.set_start_scale(1)
        self.set_end_scale(0.1)
