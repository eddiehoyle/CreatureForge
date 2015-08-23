#!/usr/bin/env python


def exists(func, *args, **kwargs):
    print "func:", func, args, kwargs
    def wraps(*args, **kwargs):
        print "args:", args, kwargs
        val = func(*args, **kwargs)
        return val

    w = wraps
    print "wraps:", w
    result = w()
    print "result:", result
    return w


def simple_decorator(decorator):
    '''This decorator can be used to turn simple functions
    into well-behaved decorators, so long as the decorators
    are fairly simple. If a decorator expects a function and
    returns a function (no descriptors), and if it doesn't
    modify function attributes or docstring, then it is
    eligible to use this. Simply apply @simple_decorator to
    your decorator and it will automatically preserve the
    docstring and function attributes of functions to which
    it is applied.'''
    def new_decorator(f):
        g = decorator(f)
        g.__name__ = f.__name__
        g.__doc__ = f.__doc__
        g.__dict__.update(f.__dict__)
        return g
    # Now a few lines needed to make simple_decorator itself
    # be a well-behaved decorator.
    new_decorator.__name__ = decorator.__name__
    new_decorator.__doc__ = decorator.__doc__
    new_decorator.__dict__.update(decorator.__dict__)
    return new_decorator

#
# Sample Use:
#
@simple_decorator
def my_simple_logging_decorator(func):
    def you_will_never_see_this_name(*args, **kwargs):
        print 'calling {}'.format(func.__name__)
        return func(*args, **kwargs)
    return you_will_never_see_this_name

class Guide(object):

    def __init__(self):
        self.__tendons = ["aaa"]

    @my_simple_logging_decorator
    def tendons(self):
        return self.__tendons

print Guide().tendons
