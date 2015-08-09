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


class Module(object):
    """
    Base Maya node.
    """

    SUFFIX = "nde"

    def __init__(self, position, description, index=0):

        self.__name = NameHandler(position,
                                  description,
                                  index=index,
                                  suffix=self.SUFFIX)
        self.__node = self.__name.compile()

        self._dag = {}
        self._nondag = {}

    def __eq__(self, other):
        return str(self.node) == str(other)

    def __str__(self):
        return self.node

    def __repr__(self):
        return "<%s '%s'>" % (self.__class__.__name__, self.node)

    def __hash__(self):
        return hash(self.node)

    def __getitem__(self, index):
        return self.node[index]

    @property
    def dag(self):
        if not self._dag:
            self._dag = json.loads(libattr.get(self.node, "dag"))
        return self._dag

    @property
    def nondag(self):
        if not self._nondag:
            self._nondag = json.loads(libattr.get(self.node, "nondag"))
        return self._nondag

    @property
    def tokens(self):
        return (self.position, self.description, self.index)

    @property
    def exists(self):
        return cmds.objExists(self.node)

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

    @property
    def snapshot(self):
        raise NotImplementedError()

    def reinit(self):
        raise NotImplementedError()

    def create(self):
        self._pre()
        self._create()
        self._post()

    def _pre(self):
        self.store("node", self.node)

    def _create(self):
        raise NotImplementedError()

    def _post(self):
        if not libattr.has(self.node, "dag"):
            libattr.add_string(self.node, "dag")
        if not libattr.has(self.node, "nondag"):
            libattr.add_string(self.node, "nondag")

        _dag = libutil.stringify(deepcopy(self._dag))
        _nondag = libutil.stringify(deepcopy(self._nondag))

        libattr.set(self.node, "dag", json.dumps(_dag), type="string")
        libattr.set(self.node, "nondag", json.dumps(_nondag), type="string")

        libattr.lock(self.node, "dag")
        libattr.lock(self.node, "nondag")

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
