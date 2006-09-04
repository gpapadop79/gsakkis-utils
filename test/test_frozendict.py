#!/usr/bin/env python

__author__ = 'George Sakkis <gsakkis@rutgers.edu>'

import unittest
from datastructs.frozendict import *


class FrozenDictTestCase(unittest.TestCase):
    def test_frozendict(self):
        self.assertEquals(frozendict(), {})
        self.assertEquals(frozendict((['x',1],['y',2])), {'x':1, 'y':2})
        self.assertEquals(frozendict({'x':1,'y':2}), {'x':1,'y':2})
        self.assertEquals(frozendict(x=1,y=2), {'x':1,'y':2})
        d = frozendict()
        self.assertRaises(TypeError, d.__setitem__, 'x', 2)
        self.assertRaises(TypeError, d.__delitem__, 'x')
        self.assertRaises(TypeError, d.clear)
        self.assertRaises(TypeError, d.setdefault, 'x', 2)
        self.assertRaises(TypeError, d.popitem)
        self.assertRaises(TypeError, d.update, {})
        # a frozendict can be a key to a dict
        self.assertEquals(len({d:1, d:2}), 1)


if __name__ == '__main__':
    unittest.main()
