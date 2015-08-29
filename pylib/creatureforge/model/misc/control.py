#!/usr/bin/env python

"""
"""

from maya import cmds
from creatureforge.model.base import Module

class Shapes:
    # SQUARE = [((-1, 0, 1,), (-1, 0, -1), (1, 0, -1), (1, 0, 1), (-1, 0, 1))]
    # CIRCLE = [((6.123233995736766e-17, 2.2204460492503131e-16, 1.0), (-0.25881904510252068, 2.1447861848524059e-16, 0.96592582628906831), (-0.49999999999999989, 1.9229626863835641e-16, 0.86602540378443871), (-0.70710678118654746, 1.5700924586837752e-16, 0.70710678118654757), (-0.8660254037844386, 1.1102230246251568e-16, 0.50000000000000011), (-0.9659258262890682, 5.7469372616863126e-17, 0.25881904510252096), (-1.0, 6.2900117310782151e-32, 2.8327694488239898e-16), (-0.96592582628906842, -5.7469372616863015e-17, -0.25881904510252046), (-0.86602540378443893, -1.1102230246251559e-16, -0.49999999999999972), (-0.70710678118654791, -1.5700924586837747e-16, -0.70710678118654735), (-0.50000000000000044, -1.9229626863835638e-16, -0.8660254037844386), (-0.25881904510252129, -2.1447861848524059e-16, -0.96592582628906831), (-5.330771254230592e-16, -2.2204460492503136e-16, -1.0000000000000002), (0.2588190451025203, -2.1447861848524067e-16, -0.96592582628906865), (0.49999999999999961, -1.922962686383565e-16, -0.86602540378443915), (0.70710678118654735, -1.5700924586837764e-16, -0.70710678118654813), (0.8660254037844386, -1.110223024625158e-16, -0.50000000000000067), (0.96592582628906842, -5.7469372616863249e-17, -0.25881904510252152), (1.0000000000000004, -1.6150773046340863e-31, -7.273661547324616e-16), (0.96592582628906898, 5.7469372616862941e-17, 0.25881904510252013), (0.86602540378443948, 1.1102230246251556e-16, 0.49999999999999956), (0.70710678118654846, 1.5700924586837747e-16, 0.70710678118654735), (0.500000000000001, 1.9229626863835641e-16, 0.86602540378443871), (0.25881904510252179, 2.1447861848524064e-16, 0.96592582628906853), (9.49410759657493e-16, 2.2204460492503141e-16, 1.0000000000000004))]
    # SPHERE = [((6.123233995736766e-17, 1.0, 0.0), (-0.25881904510252068, 0.96592582628906831, 0.0), (-0.49999999999999989, 0.86602540378443871, 0.0), (-0.70710678118654746, 0.70710678118654757, 0.0), (-0.8660254037844386, 0.50000000000000011, 0.0), (-0.9659258262890682, 0.25881904510252096, 0.0), (-1.0, 2.8327694488239898e-16, 0.0), (-0.96592582628906842, -0.25881904510252046, 0.0), (-0.86602540378443893, -0.49999999999999972, 0.0), (-0.70710678118654791, -0.70710678118654735, 0.0), (-0.50000000000000044, -0.8660254037844386, 0.0), (-0.25881904510252129, -0.96592582628906831, 0.0), (-5.330771254230592e-16, -1.0000000000000002, 0.0), (0.2588190451025203, -0.96592582628906865, 0.0), (0.49999999999999961, -0.86602540378443915, 0.0), (0.70710678118654735, -0.70710678118654813, 0.0), (0.8660254037844386, -0.50000000000000067, 0.0), (0.96592582628906842, -0.25881904510252152, 0.0), (1.0000000000000004, -7.273661547324616e-16, 0.0), (0.96592582628906898, 0.25881904510252013, 0.0), (0.86602540378443948, 0.49999999999999956, 0.0), (0.70710678118654846, 0.70710678118654735, 0.0), (0.500000000000001, 0.86602540378443871, 0.0), (0.25881904510252179, 0.96592582628906853, 0.0), (9.49410759657493e-16, 1.0000000000000004, 0.0)),
    # SEMI_CIRCLE = [[[6.123233995736766e-17, 2.2204460492503131e-16, 1.0], [-0.25881904510252068, 2.1447861848524059e-16, 0.96592582628906831], [-0.49999999999999989, 1.9229626863835641e-16, 0.86602540378443871], [-0.70710678118654746, 1.5700924586837752e-16, 0.70710678118654757], [-0.8660254037844386, 1.1102230246251568e-16, 0.50000000000000011], [-0.9659258262890682, 5.7469372616863126e-17, 0.25881904510252096], [-1.0, 6.2900117310782151e-32, 2.8327694488239898e-16], [-0.96592582628906842, -5.7469372616863015e-17, -0.25881904510252046], [-0.86602540378443893, -1.1102230246251559e-16, -0.49999999999999972], [-0.70710678118654791, -1.5700924586837747e-16, -0.70710678118654735], [-0.50000000000000044, -1.9229626863835638e-16, -0.8660254037844386], [-0.25881904510252129, -2.1447861848524059e-16, -0.96592582628906831], [-5.330771254230592e-16, -2.2204460492503136e-16, -1.0000000000000002]]]
    # PYRAMID = [[[0.0, 0.53995001316070557, 0.0], [-1.0, -1.0, 1.0], [-1.0, -1.0, -1.0], [0.0, 0.53995001316070557, 0.0], [-1.0, -1.0, -1.0], [1.0, -1.0, -1.0], [0.0, 0.53995001316070557, 0.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [0.0, 0.53995001316070557, 0.0], [1.0, -1.0, 1.0], [-1.0, -1.0, 1.0]]]
    # CUBE = [[[-1.0, 1.0, -1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0], [-1.0, 1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, -1.0, -1.0], [1.0, -1.0, -1.0], [1.0, 1.0, -1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, 1.0], [1.0, -1.0, 1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, 1.0], [-1.0, -1.0, 1.0], [-1.0, -1.0, -1.0]]]
    # CROSS = [[[-0.33310534961812344, 0.0, 0.33310534961812344], [-0.99931604885437031, 0.0, 0.33310534961812344], [-0.99931604885437031, 0.0, -0.33310534961812344], [-0.33310534961812344, 0.0, -0.33310534961812344], [-0.33310534961812344, 0.0, -0.99931604885437031], [0.33310534961812344, 0.0, -0.99931604885437031], [0.33310534961812344, 0.0, -0.33310534961812344], [0.99931604885437031, 0.0, -0.33310534961812344], [0.99931604885437031, 0.0, 0.33310534961812344], [0.33310534961812344, 0.0, 0.33310534961812344], [0.33310534961812344, 0.0, 0.99931604885437031], [-0.33310534961812344, 0.0, 0.99931604885437031], [-0.33310534961812344, 0.0, 0.33310534961812344]]]
    # ARROW_SINGLE = [[[-1.0, 0.0, 1.0], [-1.0, 0.0, -1.0], [-2.0, 0.0, -1.0], [0.0, 0.0, -3.0], [2.0, 0.0, -1.0], [1.0, 0.0, -1.0], [1.0, 0.0, 1.0], [-1.0, 0.0, 1.0]]]
    # ARROW_DOUBLE = [[[-1.0, 0.0, 2.0], [-1.0, 0.0, -1.0], [-2.0, 0.0, -1.0], [0.0, 0.0, -3.0], [2.0, 0.0, -1.0], [1.0, 0.0, -1.0], [1.0, 0.0, 2.0], [2.0, 0.0, 2.0], [0.0, 0.0, 4.0], [-2.0, 0.0, 2.0], [-1.0, 0.0, 2.0]]]
    # ARROW_TRIPLE = [[[-1.0, 0.0, 1.0], [-1.0, 0.0, 3.0], [-2.0, 0.0, 3.0], [0.0, 0.0, 5.0], [2.0, 0.0, 3.0], [1.0, 0.0, 3.0], [1.0, 0.0, -3.0], [2.0, 0.0, -3.0], [0.0, 0.0, -5.0], [-2.0, 0.0, -3.0], [-1.0, 0.0, -3.0], [-1.0, 0.0, -1.0], [-3.0, 0.0, -1.0], [-3.0, 0.0, -2.0], [-5.0, 0.0, 0.0], [-3.0, 0.0, 2.0], [-3.0, 0.0, 1.0], [-1.0, 0.0, 1.0]]]
    # ARROW_QUAD = [[[-1.0, 0.0, -1.0], [-1.0, 0.0, -3.0], [-2.0, 0.0, -3.0], [0.0, 0.0, -5.0], [2.0, 0.0, -3.0], [1.0, 0.0, -3.0], [1.0, 0.0, -1.0], [3.0, 0.0, -1.0], [3.0, 0.0, -2.0], [5.0, 0.0, 0.0], [3.0, 0.0, 2.0], [3.0, 0.0, 1.0], [1.0, 0.0, 1.0], [1.0, 0.0, 3.0], [2.0, 0.0, 3.0], [0.0, 0.0, 5.0], [-2.0, 0.0, 3.0], [-1.0, 0.0, 3.0], [-1.0, 0.0, 1.0], [-3.0, 0.0, 1.0], [-3.0, 0.0, 2.0], [-5.0, 0.0, 0.0], [-3.0, 0.0, -2.0], [-3.0, 0.0, -1.0], [-1.0, 0.0, -1.0]]]

    CIRCLE = [[[0.0, 0.0, 1.0], [-0.26, 0.0, 0.97], [-0.5, 0.0, 0.87],
               [-0.71, 0.0, 0.71], [-0.87, 0.0, 0.5], [-0.97, 0.0, 0.26],
               [-1.0, 0.0, 0.0], [-0.97, -0.0, -0.26], [-0.87, -0.0, -0.5],
               [-0.71, -0.0, -0.71], [-0.5, -0.0, -0.87], [-0.26, -0.0, -0.97],
               [-0.0, -0.0, -1.0], [0.26, -0.0, -0.97], [0.5, -0.0, -0.87],
               [0.71, -0.0, -0.71], [0.87, -0.0, -0.5], [0.97, -0.0, -0.26],
               [1.0, -0.0, -0.0], [0.97, 0.0, 0.26], [0.87, 0.0, 0.5],
               [0.71, 0.0, 0.71], [0.5, 0.0, 0.87], [0.26, 0.0, 0.97],
               [0.0, 0.0, 1.0]]]


def get_cvs(shape):
    try:
        return getattr(Shapes, str(shape).upper())
    except AttributeError:
        err = "Invalid shape: '{shape}'".format(shape=shape)
        raise RuntimeError(err)

class ControlTransformModel(Module):

    SUFFIX = "ctl"

    def __init__(self, position, description, index=0):
        super(ControlTransformModel, self).__init__(position, description, index=index)

        self.__cvs = []

    def rebuild(self):
        err = "Rebuild not written yet"
        raise NotImplementedError(err)

    def set_shape(self, shape):
        self.__cvs = get_cvs(shape)

        if self.exists():
            self.rebuild()

    def __create_node(self):

        cmds.select(cl=True)
        cmds.createNode("transform", name=self.get_name().compile())

    def _create(self):
        self.__create_node()


class ControlShapeModel(object):

    def __init__(self, control):
        self.__control = control
