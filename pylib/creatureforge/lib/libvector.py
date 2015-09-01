#!/usr/bin/env python

def add_3f(array0, array1):
    return [array0[0] + array1[0],
            array0[1] + array1[1],
            array0[2] + array1[2]]

def average_3f(array0, array1):
    return [(array0[0] + array1[0]) / 2,
            (array0[1] + array1[1]) / 2,
            (array0[2] + array1[2]) / 2]

def average_vector3f(vectors):
    """Average vectors into single vector"""

    x, y, z = 0, 0, 0
    for vector in vectors:
        x += vector[0]
        y += vector[1]
        z += vector[2]

    count = len(vectors)
    return [x/count, y/count, z/count]

def inverse3f(vector):
    return [vector[0] * -1, vector[1] * -1, vector[2] * -1]
