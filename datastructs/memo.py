'''Memoization and Memento patterns.

The memoization pattern allows a computationally expensive callable to
cache its results for fast recovery; later calls with the same arguments may
be recovered from the cache instead of being computed again. The L{Memoize}
class wraps a function f into a callable proxy instance that caches
transparently f's results. In addition, the L{memoizedmethod} function can be
used within a class definition to wrap a newly defined method as a memoized
proxy method.

The memento pattern is essentially the application of memoization for factory
functions, functions that generate instances (not necessarily new). Here the
pattern is implemented as the L{Memento} metaclass.

'''

import types

from datastructs.frozendict import frozendict, Empty as EmptyDict

__author__ = "George Sakkis <gsakkis@rutgers.edu>"
__all__ = ["Memoize", "Memento", "memoizedmethod"]


#=============================================================================

# the default class to be used for caching the function results
_defaultcache = dict


class Memoize:
    '''An implementation of the memoization pattern.'''

    def __init__(self, function, cacheFactory=_defaultcache, makeHashable=None):
        '''Memoize a function.

        @param function: The function to be memoized.
        @param cacheFactory: A callable that returns a cache object when called
            without arguments. The protocol of a cache object must provide at
            least __getitem__(key) and __setitem__(key,value).
        @param makeHashable: A callable f(*args, **kwds) that returns a hashable
            representation of args and kwds if the latter are not hashable.
            Leave it to None if args and kwds are expected to be hashable always.
        '''
        self._cache = cacheFactory()
        self._callable = function
        self._makeHashable = makeHashable

    def __call__(self, *args, **kwds):
        '''
        Return the cached value of for the given arguments, or if it is not
        cached, call the memoized callable and cache the computed value.
        '''
        cache = self._cache
        if self._makeHashable is None:
            key = self._getKey(*args,**kwds)
        else:
            key = self._makeHashable(*args,**kwds)
        try: return cache[key]
        except KeyError:
            cachedValue = cache[key] = self._callable(*args,**kwds)
            return cachedValue

    def _getKey(self,*args,**kwds):
        '''Return the cache key for a function call with the given arguments.'''
        if kwds:
            return (args, frozendict(kwds))
        if not (len(args) == 2 and \
                isinstance(args[0],tuple) and \
                isinstance(args[1],frozendict)):
            return args
        return (args, EmptyDict)


def memoizedmethod(function, cacheFactory=_defaultcache, makeHashable=None):
    '''Create a memoized proxy method from a function.

    This function is to be called from within a class definition, exactly as
    the builtins staticmethod and classmethod::
        class Foo:
            def foo(...):
                ...
            foo = memoizedmethod(foo)

    In python 2.4+, it can be declared equivalently using the decorator syntax::
        class Foo:
            @memoizedmethod
            def foo(...):
                ...

    @requires: python 2.3+.
    '''
    return types.MethodType(Memoize(function,cacheFactory,makeHashable), None)


class Memento(type):
    '''The memento pattern.

    Classes having this as metaclass create at most once an instance for a
    given constructor argument list; all subsequent instantiation calls with
    the same argument list will return the same instance.

    @requires: python 2.2+.
    '''
    __call__ = memoizedmethod(type.__call__)
