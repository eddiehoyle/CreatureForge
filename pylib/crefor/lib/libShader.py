#!/usr/bin/env python

'''
'''

from maya import cmds

def get_rgb_from_position(position):
    '''
    '''

    if position.upper().startswith('L'):
        color = (0, 0, 1)
    elif position.upper().startswith('R'):
        color = (1, 0, 0)
    elif position.upper().startswith('C'):
        color = (1, 1, 0)
    else:
        color = (0, 0, 0)
    return color

def get_shader(name):
    '''
    '''

    if cmds.objExists(name):
        return name, cmds.listConnections(name, type='shadingEngine')[0]
    return None

def get_or_create_shader(name, shader_type):
    '''
    '''

    if cmds.objExists(name):
        shader, sg = get_shader(name)
        if cmds.nodeType(shader) == shader_type:
            return shader, sg
        else:
            raise NameError('Name already exists: %s (%s)' % (name),
                                                              cmds.nodeType(name))
    else:
        return create_shader(name, shader_type)

def create_shader(name, shader_type):
    '''
    '''

    if cmds.objExists(name):
            raise NameError('Name already exists: %s (%s)' % (name),
                                                              cmds.nodeType(name))

    shader = cmds.shadingNode(shader_type, asShader=True, name=name)
    sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name='%sSG' % shader)
    cmds.connectAttr('%s.outColor' % shader, '%s.surfaceShader' % sg)
    return [shader, sg]
