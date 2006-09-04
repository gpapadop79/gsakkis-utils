'''Useful functions for map-like objects.

For the purposes os this module, a map-like object is an:
    - iterable over (key,value) pairs
    - or has a method 'iteritems' so that x.iteritems() returns an
      iterable over (key,value) pairs

@sort: reduceMappings, addMappings, makeDict, invertMapping
'''

import operator
from common.future import *

__author__ = "George Sakkis <gsakkis@rutgers.edu>"
__all__ = ["defaultdict", "reduceMappings", "addMappings", "makeDict",
           "invertMapping"]



def defaultdict(defaultfactory):
    '''Return a dict with default value for missing entries.'''
    class defdict(dict):
        def __getitem__(self, key):
            try: return super(defdict, self).__getitem__(key)
            except KeyError:
                return self.setdefault(key, defaultfactory())
    return defdict


def reduceMappings(binOp, mappings):
    '''Similar to the builtin reduce() for map-like objects.

    Return a dict with keys the union of the keys in all mappings.
    The value for each key is result of cumulatively applying the
    function binOp to all the values of that key in all mappings. The
    order of application is from the leftmost mapping to the rightmost.

    @param binOp: A callable f(x,y) -> z for accumulating the values of
        the mappings.
    @param mappings: Zero or more map-like objects.
    '''
    reduced = {}
    for mapping in mappings:
        for k,v in _mapIterator(mapping):
            try:
                reduced[k] = binOp(reduced[k], v)
            except KeyError:
                reduced[k] = v
    return reduced


def addMappings(*mappings):
    '''Shortcut for "reduceMappings(operator.add, mappings)".'''
    return reduceMappings(operator.add, mappings)


def makeDict(iterable,
             getKeyValue = lambda item:item[:2],
             itemErrorHandler = None,
             uniqueKeys = False,
             uniqueKeysErrorHandler = None):
    '''Create a dict from an iterable.

    @param iterable: Any iterable object.
    @param getKeyValue: A callable f(item) that returns a sequence of length
        2, the key and the value for this item.
    @param itemErrorHandler: A callable f(item) to be called when
        getKeyValue(item) raises Exception or does not return a (key,value)
        pair. By default, exceptions are silently ignored.
    @param uniqueKeys: True if the iterable is not supposed to have the same
        key associated with more than one value.
    @param uniqueKeysErrorHandler: A callable f(key,value,oldValue) to be
        called when uniqueKeys is True and key is associated with more than
        one values (namely, value and oldValue). By default, oldValue is
        overwritten by value if uniqueKeys is False; if not, KeyError is raised.
    '''
    mapping = {}
    for item in iterable:
        try:
            key,value = getKeyValue(item)
        except:
            if itemErrorHandler is not None:
                itemErrorHandler(item)
            else:
                raise
        else:
            _addEntry(mapping,key,value,uniqueKeys,uniqueKeysErrorHandler)
    return mapping


def invertMapping(mapping, uniqueKeysErrorHandler = None):
    '''
    Return a dictionary with keys the values of the given mapping and
    values the respective keys.

    The mapping should be 1-1; if more than one keys in the original
    mapping are mapped to the same value, uniqueKeysErrorHandler is called
    (or KeyError is raised if uniqueKeysErrorHandler is None).

    @param mapping: A map-like object.
    @param uniqueKeysErrorHandler: A callable f(value,key1,key2) to be called
        when two keys of mapping are associated to (the same) value. If None,
        a KeyError is raised.
    '''
    inverted = {}
    for k,v in _mapIterator(mapping):
        _addEntry(inverted,v,k,True,uniqueKeysErrorHandler)
    return inverted


def _mapIterator(mapping):
    try: return mapping.iteritems()
    except AttributeError: return mapping


def _addEntry(mapping, key, value, uniqueKeys = False,
             uniqueKeysErrorHandler = None):
    '''Try to add a (key,value) entry to mapping.

    @param mapping: A map-like object.
    @param key: The key of the entry to be added. It must be a hashable object.
    @param value: The value of the entry to be added.
    @param uniqueKeys: True if the mapping is not supposed to have key
        associated with a different value.
    @param uniqueKeysErrorHandler: A callable f(key,value,oldValue) to be
        called if uniqueKeys and mapping[key] == oldValue and oldValue != value.
        By default, oldValue is overwritten by value if uniqueKeys is False;
        if not, a KeyError is raised.
    '''
    try:
        oldValue = mapping[key]
    except KeyError:
        mapping[key] = value
    else:
        if not uniqueKeys:
            mapping[key] = value
        elif oldValue != value:
            if uniqueKeysErrorHandler is not None:
                uniqueKeysErrorHandler(key,value,oldValue)
            else:
                raise KeyError, "Tried to remap key '%s' to '%s' " \
                                "[currently mapped to '%s']" % (key,
                                                                value,
                                                                oldValue)
