#!/usr/bin/env python

"""
"""

from maya import cmds

from creatureforge.lib import libname
from creatureforge.model.base import Node


class Guide(Node):

    SUFFIX = "gde"

    def __init__(self, position, description, index=0):
        super(Guide, self).__init__(position, description, index)

        # self.__up = None
        # self.__aim = None
        # self.__setup = None

    @property
    def aim(self):
        return self._dag.get("aim")

    @property
    def up(self):
        return self._dag.get("up")

    @property
    def setup(self):
        return self._dag.get("setup")

    @property
    def shapes(self):
        return self._dag.get("shapes")

    def __create_setup(self):
        name = libname.rename(self.node, suffix="setup")
        setup = cmds.createNode("transform", name=name)
        self._record("setup", setup)

    def __create_node(self):
        sphere = cmds.sphere(name=self.node)[0]
        shapes = cmds.listRelatives(sphere, shapes=True)
        self._record("node", sphere)
        self._record("shapes", shapes, append=True)

    def __create_aim(self):
        name = libname.rename(self.node, suffix="aim")
        aim = cmds.createNode("transform", name=name)
        self._record("aim", aim)

    def __create_up(self):
        up = Up(self)
        up.create()
        self._record("up", up)

    def __setup_network(self):
        cmds.parent([self.aim, self.up.grp], self.setup)

    def _create(self):
        self.__create_setup()
        self.__create_node()
        self.__create_aim()
        self.__create_up()

        self.__setup_network()


class Up(Node):

    SUFFIX = "up"

    def __init__(self, guide):

        self.__guide = guide

        super(Up, self).__init__(*guide.tokens)

    @property
    def guide(self):
        return self.__guide

    @property
    def grp(self):
        return self._dag.get("grp")

    @property
    def shapes(self):
        return self._dag.get("shapes")

    def __create_node(self):
        grp_name = libname.rename(self.node, append="Up", suffix="grp")
        grp = cmds.createNode("transform", name=grp_name)
        self._record("grp", grp)

        sphere = cmds.sphere(name=self.node)[0]
        shapes = cmds.listRelatives(sphere, shapes=True)

        self._record("node", sphere)
        self._record("shapes", shapes, append=shapes)

        cmds.parent(sphere, grp)

    def _create(self):
        self.__create_node()


class Connector(Node):

    SUFFIX = "cnc"

    def __init__(self, child, parent):
        pass
