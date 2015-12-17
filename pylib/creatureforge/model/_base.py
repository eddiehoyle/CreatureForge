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
from creatureforge.lib import libname

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
    """Base class for all models.
    """

    SUFFIX = "nde"

    def __init__(self, name, **kwargs):
        self.__name = libname.rename(libname.init(name), suffix=self.SUFFIX)

        # self.__name = NameModel(position,
        #                         primary,
        #                         primary_index,
        #                         secondary,
        #                         secondary_index,
        #                         suffix=self.SUFFIX)

        self._dag = {}
        self._nondag = {}
        self._meta = {}

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
        return str(self.name)

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

        self.__pre_create()
        self._create()
        self.__post_create()

        cmds.select(self.node, r=True)

    def __pre_create(self):
        """Create model node(s).
        """

        node = cmds.createNode("transform", name=self.name)
        libattr.add_string(node, "dag")
        libattr.add_string(node, "nondag")
        libattr.add_string(node, "meta")

    def _create(self):
        raise NotImplementedError("_create")

    def __post_create(self):
        """Store container data into nodes
        """
        return

    def remove(self):
        """Delete all traces of module from scene.
        """

        dag = list(libutil.flatten(self.dag.values()))
        nondag = list(libutil.flatten(self.nondag.values()))

        if dag:
            cmds.delete(dag)
        if nondag:
            cmds.delete(nondag)

        self._dag = self._nondag = self._meta = {}

        print "Deleted {0} node(s).".format(len(dag + nondag))


class ModuleModelDynamicBase(ModuleModelBase):
    """User facing models?
    """

    def __post_create(self):
        """Store container data into nodes
        """

        self._refresh("dag")
        self._refresh("nondag")
        self._refresh("meta")

    def _refresh(self, container):
        """Refresh a container
        """
        libattr.unlock(self.node, container)
        data = json.loads(libattr.get(self.node, container) or "{}")
        data.update(getattr(self, container) or {})
        libattr.set(self.node, container, json.dumps(
            libutil.stringify(data)), type="string")
        libattr.lock(self.node, "dag")

    def store(self, key, value, container="dag", append=False):
        container_map = {
            "dag": self._dag,
            "nondag": self._nondag,
            "meta": self._meta
        }
        data = container_map[container]
        if append:
            if key not in data:
                data[key] = []
            if isinstance(value, (list, tuple, set)):
                data[key].extend(value)
            else:
                data[key].append(value)
        else:
            data[key] = value
        if self.exists:
            self._refresh(container)


class ModuleModelStaticBase(ModuleModelBase):
    pass
