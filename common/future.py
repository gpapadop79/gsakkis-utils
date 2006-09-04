'''Provides (partial) forward compatibility to python/jython 2.1+.

This module redefines several useful names that are builtin in newer
python versions (2.3+) so that they can be accessed in earlier versions
as well. This includes:
    - True, False
    - Primitive factory functions (int,float, etc.) being bound to the
      respective type (types.IntType, types.FloatType, etc.). Unfortunately
      this forward compatibility attempt is partially successful in jython
      2.1 because type constructors do not in general have the same behavior
      as the repsective factory functions (e.g. types.ListType((1,2)) !=
      list((1,2))). Rebinding the __init__ of each type does not work either.
      (XXX: this whole idea is error prone and maybe should be ditched...)
    - enumerate (bultin since python 2.3)
    - dict.iteritems and dict.pop (todo: dict.iterkeys, dict.itervalues).
      Python 2.2 does not allow modifying a builtin type such as dict, so
      dict.pop cannot be added.

@todo: Add dict.iterkeys,dict.itervalues
'''

from __future__ import nested_scopes
import sys,types

__author__ = "George Sakkis <gsakkis@rutgers.edu>"
__all__ = ["False", "True", "enumerate",
           "int", "float", "str", "tuple", "list", "dict", "type", "bool"]

##############################################################################

def _pop(self,key,default=None):
    '''
    Pop the entry with the given key from the dictionary and return the
    respective value [dict method since python 2.3].
    '''
    try:
        val = self[key]
        del self[key]
        return val
    except KeyError:
        if default is None:
            raise
        return default

def _iteritems(self):
    '''Iterator version of dict.items() [dict method since python 2.2].'''
    # i don't know if it's possible to iterate on a dict without copying
    # at least the keys in python < 2.2...
    keys = self.keys()
    class ItemIterator:
        def __len__(my):
            return len(keys)
        def __getitem__(my,pos):
            key = keys[pos]
            return key, self[key]
    return ItemIterator()

try: iter
except NameError:
    # no iterators (version < 2.2)
    def _enumerate(iterable):
        '''Iterator for index,value of iterable [builtin since python 2.3].'''
        class Enumerator:
            def __init__(self):
                self._count = 0
            def __getitem__(self,pos):
                pair = self._count, iterable[self._count]
                self._count += 1
                return pair
        return Enumerator()
else:
    def _enumerate(iterable):
        '''Iterator for index,value of iterable [builtin since python 2.3].'''
        class Enumerator:
            def __init__(self):
                self._count = 0
                self._compIter = iter(iterable)
            def __iter__(self):
                return self
            def next(self):
                pair = self._count, self._compIter.next()
                self._count += 1
                return pair
        return Enumerator()

#########################################################################

# CAVEAT: In jython 2.1, the constructors of the primitive types do not
# behave as the respective builtin factory functions (as of python 2.2).
# Replacing __init__ does not work either because constructors are
# cached methods ... :-(

for name, value in [
    ("False" , 0),
    ("True"  , 1),
    ("int"   , types.IntType),
    ("float" , types.FloatType),
    ("str"   , types.StringType),
    ("tuple" , types.TupleType),
    ("list"  , types.ListType),
    ("dict"  , types.DictType),
    ("type"  , types.TypeType),
    ("bool"  , lambda x: x and True or False),
    ("enumerate", _enumerate)]:
        setattr(sys.modules[__name__],name,value)

# XXX: python 2.2 does not allow modifying a builtin type such as dict
for name,value in [
    ("pop", _pop),
    ("iteritems", _iteritems)]:
    if not hasattr(dict,name):
        try: setattr(dict,name,value)
        except: pass

#########################################################################

del sys, types
