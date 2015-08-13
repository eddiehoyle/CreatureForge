#!/usr/bin/env python

# from maya importmemoize cmds


def exists(func):
    def wraps(*args, **kwargs):
        if not cmds.objExists(str(args[0])):
            raise Exception("Nooo")
        return func(*args, **kwargs)
    return wraps


class Decorator(object):
    pass


class Cache(object):
    def __init__(self, func):
        self.func = func
        for name in set(dir(func)) - set(dir(self)):
            setattr(self, name, getattr(func, name))

    def __call__(self, *args):
        return self.func(*args)


def memoize(f):
    """
    Memoization decorator for functions taking one or more arguments.
    """

    class Memodict(dict):
        def __init__(self, f):
            self.f = f

        def __call__(self, *args):
            return self[args]

        def __missing__(self, key):
            ret = self[key] = self.f(*key)
            return ret

    return Memodict(f)

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



# fib(4, a=123, b=None, c=[])

# import timeit
# from functools import partial
# times = timeit.Timer(partial(fib, 3)).repeat(3, 1000000)
# print min(times), max(times)