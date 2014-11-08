#!/usr/bin/env python

'''
'''

from maya import cmds
from crefor.model import Node
from crefor.lib import libName, libShader, libAttr

class Connector(Node):

    SUFFIX = 'cnc'
    RADIUS = 0.4
    DASHED_COUNT = 5
    DEFAULT_AXIS = 'X'

    def __init__(self, parent, child):
        super(Connector, self).__init__(*libName._decompile(child.name)[:-1])

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

        self.__aim_transform = None
        self.__aim_shapes = []
        
        self.state_node = None

        self.shaders = {}

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
            cmds.sets(self.__aim_shapes, edit=True, forceElement=sg)

    @property
    def transform(self):
        if self.__solid_transform and self.__dashed_transform:
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

    def get_parent(self):
        return self.parent

    def get_child(self):
        return self.child

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

        # Create cone
        self.__aim_transform = cmds.polyCone(name=libName.append_description(self.name, 'aim'),
                                               r=self.RADIUS * 2,
                                               h=(self.RADIUS * 4) * -1,
                                               sx=16,
                                               sy=0,
                                               ax=(0, 1, 0),
                                               rcp=0,
                                               cuv=3,
                                               ch=0)[0]
        self.__aim_shapes = cmds.listRelatives(self.__aim_transform, type='mesh', children=True)

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

        lattice = cmds.rename(lattice, libName.set_suffix(self.name, 'ltc'))
        lattice_handle = cmds.rename(lattice_handle, libName.set_suffix(self.name, 'lth'))
        lattice_base = cmds.rename(lattice_base, libName.set_suffix(self.name, 'ltb'))

        cmds.move(0, '%s.pt[*][*][*]' % lattice_handle, y=True)

        self.start_cl, _start = cmds.cluster(['%s.pt[0:1][1][0]' % lattice_handle, '%s.pt[0:1][1][1]' % lattice_handle])
        self.end_cl, _end = cmds.cluster(['%s.pt[0:1][0][0]' % lattice_handle, '%s.pt[0:1][0][1]' % lattice_handle])
        self.aim_cl, _aim = cmds.cluster(self.__aim_transform)

        _start = cmds.rename(_start, libName.set_suffix(libName.append_description(self.name, 'start'), 'clh'))
        _end = cmds.rename(_end, libName.set_suffix(libName.append_description(self.name, 'end'), 'clh'))
        _aim = cmds.rename(_aim, libName.set_suffix(libName.append_description(self.name, 'aim'), 'clh'))
        self.start_cl = cmds.rename('%sCluster' % _start, libName.set_suffix(libName.append_description(self.name, 'start'), 'cls'))
        self.end_cl = cmds.rename('%sCluster' % _end, libName.set_suffix(libName.append_description(self.name, 'end'), 'cls'))
        self.aim_cl = cmds.rename('%sCluster' % _aim, libName.set_suffix(libName.append_description(self.name, 'aim'), 'cls'))

        cmds.move(-0.7, _start, y=True)
        cmds.move(0.7, _end, y=True)

        # for clh in [_start, _end, _aim]:
        #     libAttr.lock_all(clh, hide=True)

        self.start = cmds.group(_start, name=libName.set_suffix(_start, '%sGrp' % libName.get_suffix(_start)))
        self.end = cmds.group(_end, name=libName.set_suffix(_end, '%sGrp' % libName.get_suffix(_end)))
        self.aim = cmds.group(_aim, name=libName.set_suffix(_aim, '%sGrp' % libName.get_suffix(_aim)))

        # for clh in [self.start, self.end, self.aim, start_grp, end_grp, aim_grp]:
        for clh in [self.start, self.end, self.aim]:
            cmds.xform(clh, piv=(0, 0, 0), ws=True)

        # Create parent constraint for arrow geo
        con = cmds.parentConstraint([self.start, self.end], self.aim, mo=False)[0]
        aliases = cmds.parentConstraint(con, q=True, wal=True)
        for alias in aliases:
            cmds.setAttr('%s.%s' % (con, alias), 1.0/len(aliases))

        cmds.aimConstraint(self.start, self.end, worldUpObject=self.child.up,
                           worldUpType='object',
                           offset=(0, 180, -90),
                           aimVector=(1, 0, 0),
                           upVector=(0, 1, 0),
                           mo=False)

        cmds.aimConstraint(self.end, self.start, worldUpObject=self.parent.up,
                           worldUpType='object',
                           offset=(0, 0, 90),
                           aimVector=(1, 0, 0),
                           upVector=(0, 1, 0),
                           mo=False)

        self.state_node = cmds.createNode('reverse')

        cmds.addAttr(self.state_node, ln='display', at='enum', en='solid:dashed', dv=0)
        cmds.setAttr('%s.display' % self.state_node, k=False)
        cmds.setAttr('%s.display' % self.state_node, cb=True)
        cmds.connectAttr('%s.display' % self.state_node, '%s.inputX' % self.state_node)

        for attr in ['inputX', 'inputY', 'inputZ']:
            cmds.setAttr('%s.%s' % (self.state_node, attr), k=False)

        cmds.connectAttr('%s.outputX' % self.state_node, '%s.visibility' % self.__solid_transform)
        cmds.connectAttr('%s.outputX' % self.state_node, '%s.visibility' % self.__aim_transform)
        cmds.connectAttr('%s.display' % self.state_node, '%s.visibility' % self.__dashed_transform)

        # Parent under parent and child grps
        cmds.parent(self.start, self.parent.transform, r=True)
        cmds.parent(self.end, self.child.transform, r=True)

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

        for shader, rgb in zip([red, green, blue, none], [(1, 0, 0), (0, 1, 0), (0, 0, 1), (0.5, 0.5, 0.5)]):
            cmds.setAttr('%s.color' % shader, *rgb, type='float3')
            cmds.setAttr('%s.incandescence' % shader, *rgb, type='float3')

        self.set_axis(self.DEFAULT_AXIS)

    def __create_attribtues(self):
        pass

    def init(self):
        pass

    def create(self):
        self.__create_geometry()
        self.__create_deformers()
        self.__create_attribtues()
        self.__create_shader()
