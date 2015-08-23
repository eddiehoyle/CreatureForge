#!/usr/bin/env python

"""
"""

import json
import logging
from copy import deepcopy

from maya import cmds

from creatureforge.lib.libname import NameHandler
from creatureforge.lib import libattr
from creatureforge.lib import libutil


# ------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------


def cache(func):
    def wraps(*args, **kwargs):
        node = args[0].node
        if not cmds.objExists(node):
            err = "Guide does not exist: '{node}'".format(node=node)
            raise RuntimeError(err)
        return func(*args, **kwargs)
    return wraps


class Module(object):
    """
    Base Maya node.
    """

    SUFFIX = "nde"

    __name__ = "Module"

    def __init__(self, position, description, index=0):

        self.__name = NameHandler(position,
                                  description,
                                  index=index,
                                  suffix=self.SUFFIX)
        self.__node = self.__name.compile()

        self._dag = {}
        self._nondag = {}

    def __eq__(self, other):
        return str(self.get_node()) == str(other)

    def __str__(self):
        return self.get_node()

    def __repr__(self):
        return "<%s '%s'>" % (self.__class__.__name__, self.get_node())

    def __hash__(self):
        return hash(self.get_node())

    def get_name(self):
        return self.__name

    @cache
    def get_node(self):
        return self.__node

    @cache
    def get_dag(self):
        if not self._dag:
            self._dag = json.loads(libattr.get(self.get_node(), "dag"))
        return self._dag

    @cache
    def get_nondag(self):
        if not self._nondag:
            self._nondag = json.loads(libattr.get(self.get_node(), "nondag"))
        return self._nondag

    def reinit(self):
        self._dag = json.loads(libattr.get(self.get_node(), "dag"))
        self._nondag = json.loads(libattr.get(self.get_node(), "nondag"))
        return self

    @property
    def long(self):
        if self.exists:
            return cmds.ls(self.get_node(), long=True)[0]
        return None

    def exists(self):
        return cmds.objExists(self.get_name().compile())

    # @property
    # def dag(self):
    #     raise RuntimeError
    #     if not self._dag:
    #         self._dag = json.loads(libattr.get(self.get_node(), "dag"))
    #     return self._dag

    # @property
    # def nondag(self):
    #     raise RuntimeError
    #     if not self._nondag:
    #         self._nondag = json.loads(libattr.get(self.get_node(), "nondag"))
    #     return self._nondag

    @property
    def tokens(self):
        return (self.position, self.description, self.index)

    @property
    def node(self):
        return self.__node

    @property
    def position(self):
        return self.__name.position

    @property
    def description(self):
        return self.__name.description

    @property
    def index(self):
        return self.__name.index

    @property
    def suffix(self):
        return self.__name.suffix

    @cache
    def remove(self):
        dags = list(libutil.flatten(self.get_dag().values()))
        nondags = list(libutil.flatten(self.get_nondag().values()))

        nodes = []
        nodes.extend(map(str, dags))
        nodes.extend(map(str, nondags))

        print "Checking nodes:", nodes

        cmds.delete(nodes)

    def create(self):
        self._pre()
        self._create()
        self._post()

    def _pre(self):
        self.store("node", self.get_name())

    def _create(self):
        raise NotImplementedError()

    def _post(self):
        if not libattr.has(self.get_node(), "dag"):
            libattr.add_string(self.get_node(), "dag")
        if not libattr.has(self.get_node(), "nondag"):
            libattr.add_string(self.get_node(), "nondag")

        _dag = libutil.stringify(deepcopy(self._dag))
        _nondag = libutil.stringify(deepcopy(self._nondag))

        libattr.set(self.get_node(), "dag", json.dumps(_dag), type="string")
        libattr.set(self.get_node(), "nondag", json.dumps(_nondag), type="string")

        libattr.lock(self.get_node(), "dag")
        libattr.lock(self.get_node(), "nondag")

    def store(self, key, value, dag=True, append=False):
        if dag:
            self.__record(self._dag, key, value, append=append)
        else:
            self.__record(self._nondag, key, value, append=append)

    def __record(self, _dict, key, value, **kwargs):
        if kwargs.get("append"):
            if key not in _dict:
                _dict[key] = []
            if isinstance(value, (list, tuple, set)):
                _dict[key].extend(value)
            else:
                _dict[key].append(value)
        else:
            _dict[key] = value
