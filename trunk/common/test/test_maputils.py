#!/usr/bin/env python

import unittest
from common import True,False
from common.maputils import *

__author__ = "George Sakkis <gsakkis@rutgers.edu>"


class MapUtilsTestCase(unittest.TestCase):
    def test_addMappings(self):
        d1 = {'a':2, 'b':3, 'c':-2}
        d2 = {'a':-3, 'c':12, 'd':4, 'f':1}
        self.assertEquals(addMappings(d1,d2),
                          {'a': -1, 'c': 10, 'b': 3, 'd': 4, 'f': 1})

    def test_reduceMappings(self):
        d1 = {'a':2, 'b':3, 'c':-2}
        d2 = {'a':-3, 'c':12, 'd':4, 'f':1}
        self.assertEquals(reduceMappings(max, [d1,d2]),
                          {'a': 2, 'c': 12, 'b': 3, 'd': 4, 'f': 1})
        from operator import sub
        self.assertEquals(reduceMappings(sub, [d1,d2]),
                          {'a': 5, 'c': -14, 'b': 3, 'd': 4, 'f': 1})

    def test_makeDict_noduplicates(self):
        seq = [(1,"x"), (2,"y"), (3,"x")]
        # use defaults
        self.assertEquals(makeDict(seq), {1:"x", 2:"y", 3:"x"})
        # same for sequence of pairs
        self.assertEquals(makeDict(seq, getKeyValue = lambda t:t),
                          {1:"x", 2:"y", 3:"x"})
        # map to new keys/values
        self.assertEquals(makeDict(seq,
                                   getKeyValue = lambda t:(t[0]*2, t[1]*2)),
                          {2:"xx", 4:"yy", 6:"xx"})
        # IndexError / no itemErrorHandler
        self.assertRaises(IndexError, makeDict, seq,
                          getKeyValue = lambda t:(t[1],t[2]))
        # ValueError (unpack sequence) / no itemErrorHandler
        self.assertRaises(ValueError, makeDict, seq,
                          getKeyValue = lambda t:t[1:])
        # Same ValueError / use itemErrorHandler to ignore errors
        self.assertEquals(makeDict(seq, getKeyValue = lambda t:t[1:],
                                   itemErrorHandler = lambda item: None),
                          {})

        # test duplicate keys
        getKeyValue=lambda t:(t[1],t[0])
        # don't force unique keys - last value set for each key remains
        self.assertEquals(makeDict(seq,
                                   getKeyValue=getKeyValue,
                                   uniqueKeys = False),
                          {"y":2, "x":3})
        # force unique keys with dummy uniqueKeysErrorHandler
        # first value set for each key remains
        self.assertEquals(makeDict(seq, getKeyValue=getKeyValue,
                                   uniqueKeys = True,
                                   uniqueKeysErrorHandler = lambda key,value,oldvalue:None),
                          {"y":2, "x":1})
        # force unique keys without uniqueKeysErrorHandler - KeyError
        self.assertRaises(KeyError, makeDict, seq,
                          getKeyValue=getKeyValue, uniqueKeys = True)

    def test_invertMapping(self):
        map = {1:"x", 2:"y"}
        self.assertEquals(invertMapping(map), {"x":1, "y":2})
        map = {1:"x", 2:"y", 3:"x"}
        self.assertRaises(KeyError, invertMapping, map)


if __name__ == '__main__':
    unittest.main()
