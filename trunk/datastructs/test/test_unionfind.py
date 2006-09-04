#!/usr/bin/env python

import unittest
from datastructs.unionfind import *

__author__ = "George Sakkis <gsakkis@rutgers.edu>"


class UnionfindTestCase(unittest.TestCase):
    def test_add(self):
        u = UnionFind()
        items = range(10)    
        for i in items:
            u.add(i)
        self.assertEquals(len(u), len(items))
        self.assertEquals(u.numSets(), len(items))
        for i in items:
            self.assertEquals(id(u[i]), id(i))
            self.assertEquals(len(u.getSet(i)), 1)
            for j in items:
                self.failUnless(i != j ^ u.inSameSet(i,j))
        # no effect on existing items
        self.assertEquals(u.add(1), u)
        # KeyError on trying to access unknown item
        self.assertRaises(KeyError, u.__getitem__, 11)    
    
    def test_union(self):
        u = UnionFind()
        items = range(9)
        for i in items:
            u.add(i)
        # unite nothing
        self.assertEquals(u.union(), u)
        # unite one item = add
        self.assertEquals(u.union(1), u)
        # unite two items
        self.failIf(u.inSameSet(0,1))
        u.union(0,1)
        self.failUnless(u.inSameSet(0,1))
        self.assertEquals(len(u), 9)
        self.assertEquals(u.numSets(), 8)
        # unite more than two items
        u.union(2,3,4)
        u.union(5,6,7,8)
        self.failUnless(u.inSameSet(2,3,4))
        self.failUnless(u.inSameSet(5,6,7,8))
        self.assertEquals(len(u), 9)
        self.assertEquals(u.numSets(), 3)
        self.assertEquals(len(list(u.iterSets())), 3)
        self.failIf(u.inSameSet(2,5))
        self.assertEquals(len(u.getSet(0)), 2)
        self.assertEquals(len(u.getSet(2)), 3)
        self.assertEquals(len(u.getSet(5)), 4)
        # unite with a new item
        u.union(0,2,9)
        self.failUnless(u.inSameSet(0,1,2,3,4,9))
        self.assertEquals(len(u), 10)
        self.assertEquals(u.numSets(), 2)
        self.assertEquals(len(u.getSet(0)), 6)
        self.assertEquals(len(u.getSet(5)), 4)
        self.assertRaises(KeyError, u.getSet, 10)
        
if __name__ == '__main__':
    unittest.main()        
