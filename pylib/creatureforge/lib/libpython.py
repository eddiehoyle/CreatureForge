#!/usr/bin/env python

import gc
import sys


def flush():
    """
    Flushes all loaded modules from sys.modules which causes them to be
    reloaded when next imported.
    """

    flush_keys = []
    for mod_name, mod_obj in sys.modules.items():

        try:
            mod_obj.__file__
        except AttributeError:
            continue

        if "creatureforge" in mod_name:
            flush_keys.append(mod_name)

    count = 0
    for key in flush_keys:
        count += 1
        del(sys.modules[key])

    print "Flushed {num} module(s)".format(num=count)

    gc.collect()
