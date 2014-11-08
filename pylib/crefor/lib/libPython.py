#!/usr/bin/env python

'''
'''

from __future__ import with_statement
import gc
import sys

def flush():
    '''
    flushes all loaded modules from sys.modules which causes them to be reloaded
    when next imported...  super useful for developing crap within a persistent
    python environment
    '''

    flush_keys = []
    for mod_name, mod_obj in sys.modules.items():

        try:
            mod_obj.__file__
        except AttributeError:
            continue

        if 'crefor' in mod_name:
            flush_keys.append(mod_name)

    count = 0
    for key in flush_keys:
        count += 1
        del( sys.modules[key] )

    print "Flushed %s module(s)" % count

    gc.collect()  #force a garbage collection
