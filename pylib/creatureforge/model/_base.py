#!/usr/bin/env python

"""
"""

import json
import logging
from copy import deepcopy

from maya import cmds

from creatureforge.model.gen.name import NameModel
from creatureforge.lib import libattr
from creatureforge.lib import libutil

logger = logging.getLogger(__name__)


def cache(func):
    def wraps(*args, **kwargs):
        node = args[0].node
        if not cmds.objExists(node):
            err = "Guide does not exist: '{node}'".format(node=node)
            raise RuntimeError(err)
        return func(*args, **kwargs)
    return wraps


class ModuleModelBase(object):

    SUFFIX = "nde"

    def __init__(self, position, primary, primary_index, secondary,
                 secondary_index):

        self.__name = NameModel(position,
                                primary,
                                primary_index,
                                secondary,
                                secondary_index,
                                suffix=self.SUFFIX)

        self._dag = {}
        self._nondag = {}
        self._meta = {}

        self.__reinit()

    def __reinit(self):
        if self.exists:
            self._dag = json.loads(libattr.get(self.node, "dag"))
            self._nondag = json.loads(libattr.get(self.node, "nondag"))

            # TODO:
            #   Reinit all values to be original types?
            self._meta = json.loads(libattr.get(self.node, "meta"))

    def __eq__(self, other):
        return str(self.name) == str(other)

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return "<%s '%s'>" % (self.__class__.__name__, self.name)

    def __hash__(self):
        return hash(str(self.name))

    @property
    def name(self):
        return self.__name

    @property
    def node(self):
        if self.exists:
            return str(self.name)
        raise RuntimeError("Node '{0}' does not exist!".format(self.name))

    @property
    def exists(self):
        return cmds.objExists(self.name)

    @property
    def dag(self):
        return deepcopy(self._dag)

    @property
    def nondag(self):
        return deepcopy(self._nondag)

    @property
    def meta(self):
        return deepcopy(self._meta)

    def create(self):
        if self.exists:
            raise RuntimeError("Model '{0}' already exists!".format(self.name))

        self._create()

        libattr.add_string(self.node, "dag")
        libattr.add_string(self.node, "nondag")
        libattr.add_string(self.node, "meta")

        self.store("node", str(self.name), container="dag")
        self.refresh()

        cmds.select(self.node, r=True)

    def refresh(self):
        """Store container data into nodes
        """

        libattr.unlock(self.node, "dag")
        libattr.unlock(self.node, "nondag")
        libattr.unlock(self.node, "meta")

        meta = json.loads(libattr.get(self.node, "meta") or "{}")
        meta.update(self.meta)
        libattr.set(self.node, "meta", json.dumps(
            libutil.stringify(meta)), type="string")

        dag = json.loads(libattr.get(self.node, "dag") or "{}")
        dag.update(self.dag)
        libattr.set(self.node, "dag", json.dumps(
            libutil.stringify(dag)), type="string")

        nondag = json.loads(libattr.get(self.node, "nondag") or "{}")
        nondag.update(self.nondag)
        libattr.set(self.node, "nondag", json.dumps(
            libutil.stringify(nondag)), type="string")

        libattr.lock(self.node, "dag")
        libattr.lock(self.node, "nondag")
        libattr.lock(self.node, "meta")

    def remove(self):
        """Delete all traces of module from scene.
        """

        dag = list(libutil.flatten(self.dag.values()))
        nondag = list(libutil.flatten(self.nondag.values()))

        if dag:
            cmds.delete(dag)
        if nondag:
            cmds.delete(nondag)

        self._dag = {}
        self._nondag = {}
        self._meta = {}

        print "Deleted {0} node(s).".format(len(dag + nondag))

    def _create(self):
        raise NotImplementedError("_create")

    def store(self, key, value, container="dag", append=False):
        container_map = {
            "dag": self._dag,
            "nondag": self._nondag,
            "meta": self._meta
        }
        container = container_map[container]
        if append:
            if key not in container:
                container[key] = []
            if isinstance(value, (list, tuple, set)):
                container[key].extend(value)
            else:
                container[key].append(value)
        else:
            container[key] = value
