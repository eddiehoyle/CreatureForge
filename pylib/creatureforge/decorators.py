#!/usr/bin/env python

from maya import cmds

import collections
import functools

def exists(func):
    def wraps(*args, **kwargs):
        if not cmds.objExists(str(args[0])):
            raise Exception("Nooo")
        return func(*args, **kwargs)
    return wraps


import time

def timeit(f):
    """Ugh, write me properly later"""
    def timed(*args, **kw):
        t = time.time()
        result = f(*args, **kw)
        msg = "%s(" % f.__name__
        if len(args) > 1:
            msg += ", ".join(map(str, args))
        else:
            if kw:
                msg += "%s, " % args
            else:
                msg += "%s" % args
        items = kw.items()
        z = map(lambda x: "%s=%s" % x, items)
        msg += ", ".join(z)

        msg += ") took %2.8fs" % (time.time() - t)
        print msg
        return result

    return timed

@timeit
def fib(n, **kwargs):
    return n if n < 2 else fib(n-1) + fib(n-2)


class Memoized(object):
    '''Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated).
    '''
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        node = args[0]
        if cmds.objExists(node):
            if not isinstance(args, collections.Hashable):
                return self.func(*args)
            if args in self.cache:
                return self.cache[args]
            else:
                value = self.func(*args)
                self.cache[args] = value
                return value
        return None

    def __repr__(self):
        '''Return the function's docstring.'''
        return self.func.__doc__

    def __get__(self, obj, objtype):
        '''Support instance methods.'''
        return functools.partial(self.__call__, obj)

    def update(self):
        pass

    def remove(self):
        pass
