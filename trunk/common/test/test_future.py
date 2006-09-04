#!/usr/bin/env python

import unittest
from common.future import *

__author__ = "George Sakkis <gsakkis@rutgers.edu>"


class FutureTestCase(unittest.TestCase):
    def test_py2_1_types(self):
        self.assertEquals(1+1==2, True)
        self.assertEquals(1+1==3, False)

        self.assert_(isinstance(2,int))
        self.assert_(isinstance(2.,float))

        self.assert_(isinstance((),tuple))
        self.assert_(isinstance((2,),tuple))

        self.assert_(isinstance([],list))
        self.assert_(isinstance([2],list))

        self.assert_(isinstance({},dict))
        self.assert_(isinstance({2:2},dict))

    def test_bool(self):
        self.assert_(bool(None) is False)
        self.assert_(bool(0) is False)
        self.assert_(bool(0.0) is False)
        self.assert_(bool(()) is False)
        self.assert_(bool([]) is False)
        self.assert_(bool({}) is False)
        self.assert_(bool("") is False)

        self.assert_(bool(2) is True)
        self.assert_(bool((None,)) is True)
        self.assert_(bool([None]) is True)
        self.assert_(bool({0:None}) is True)
        self.assert_(bool("0") is True)

    def test_pop(self):
        d = {1:"1", 2:"2"}
        self.assertEquals(d.pop(1), "1")
        self.assertEquals(d, {2:"2"})
        self.assertRaises(KeyError, d.pop, 3)
        self.assertEquals(d.pop(2), "2")
        self.assertEquals(d,{})

    def test_iteritems(self):
        keyVals = [(1,"1"), (2,"2")]
        for pair in {1:"1", 2:"2"}.iteritems():
            keyVals.remove(pair)
        self.assertEquals(keyVals,[])

    def test_enumerate(self):
        s = "abcd"
        for i,x in enumerate(s):
            self.assertEquals(ord(s[0])+i, ord(x))


if __name__ == '__main__':
    unittest.main()
