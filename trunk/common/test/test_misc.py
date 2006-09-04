#!/usr/bin/env python

import unittest
from common.misc import *

__author__ = "George Sakkis <gsakkis@rutgers.edu>"


class MiscTestCase(unittest.TestCase):
    def test_frange(self):
        self._assertAlmostEquals(frange(0.2, 0.49, 0.1), [0.2,0.3,0.4])
        self._assertAlmostEquals(frange(0.2, 0.50, 0.1), [0.2,0.3,0.4])
        self._assertAlmostEquals(frange(0.2, 0.51, 0.1), [0.2,0.3,0.4,0.5])

        self._assertAlmostEquals(frange(0.2, +0.01, -0.1), [0.2,0.1])
        self._assertAlmostEquals(frange(0.2,  0.00, -0.1), [0.2,0.1])
        self._assertAlmostEquals(frange(0.2, -0.01, -0.1), [0.2,0.1,0.0])

        self.assertEquals(frange(0.2, -0.5, 0.1), [])
        self.assertEquals(frange(0.2, 0.5, -0.1), [])

    def _assertAlmostEquals(self, seq1, seq2, places=7, msg=None):
        self.assertEquals(len(seq1), len(seq2))
        for x1,x2 in zip(seq1,seq2):
           if round(x1-x2, places) != 0:
               raise self.failureException, \
                     (msg or '%r != %r within %r places' % (x1, x2, places))


if __name__ == '__main__':
    unittest.main()
