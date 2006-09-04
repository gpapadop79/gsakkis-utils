#!/usr/bin/env python

from __future__ import nested_scopes

import unittest
from common import True,False
from common.sequenceutils import *

__author__ = "George Sakkis <gsakkis@rutgers.edu>"


class SequenceUtilsTestCase(unittest.TestCase):
    def test_sum(self):
        self.assertEquals(sum([1,2,3,4]), 10)
        self.assertEquals(sum(["this ","is ", "a ", "string"]),
                          "this is a string")
        self.assertEquals(sum([("this","is"),("a","string")]),
                          ("this","is","a","string"))
        self.assertEquals(sum([]), 0)

    def test_average(self):
        self.assertEquals(average([1,2,9]), 4)
        self.assertEquals(average([1,2,3,9]), 3.75)

    def test_median(self):
        self.assertEquals(median([1,2,9]), 2)
        self.assertEquals(median([1,2,3,9]), 2.5)

    def test_standardDeviation(self):
        self.assertEquals(round(standardDeviation([5,6,8,9], isSample=False),4), 1.5811)
        self.assertEquals(round(standardDeviation([5,6,8,9], isSample=True),4), 1.8257)

    def test_frequency(self):
        self.assertEquals(frequency("this is a string"),
                          {'t':2, 'h': 1, 'i':3, 's':3, ' ':3,
                           'a':1, 'r': 1, 'n':1, 'g':1})

    def test_uniq(self):
        self.assertEquals(uniq("this is a string"), [x for x in "this arng"])

    def test_sorted(self):
        itemgetter = lambda i: lambda seq: seq[i]
        x = (1,"z"), (7,"a"), (-3,"q"), (4, "b")
        self.assertEquals(sorted(x),
                          [(-3,"q"), (1,"z"), (4, "b"), (7,"a")])
        self.assertEquals(sorted(x, key=itemgetter(1)),
                          [(7,"a"), (4, "b"), (-3,"q"), (1,"z")])
        self.assertEquals(sorted(x, value=itemgetter(1)),
                          ["q", "z", "b", "a"])
        self.assertEquals(sorted(x, key=itemgetter(1), value=itemgetter(0)),
                          [7, 4, -3, 1])
        self.assertEquals(sorted(x, key=itemgetter(1), descending=True),
                         [(1,"z"), (-3,"q"), (4, "b"), (7,"a")])
        self.assertEquals(sorted(x, value=itemgetter(1), maxLength=2),
                         ["q", "z"])
        self.assertEquals(sorted(x, key=itemgetter(1), value=itemgetter(0),
                                 descending=True, maxLength=3),
                          [1, -3, 4])
        y = [2,1,2,3,1]
        self.assertEquals(sorted(y, maxLength=3, acceptTies=False), [1,1,2])
        self.assertEquals(sorted(y, maxLength=3, acceptTies=True), [1,1,2,2])

        z = range(10) * 2
        self.assert_(sorted(z, inPlace=False) is not z)
        self.assert_(sorted(z, inPlace=True) is z)

    def test_groupBy(self):
        info = [line.split() for line in
                "Tom Jones C 32 85823.956",
                "Dave Lombardo D 26 9694.57",
                "Mary Baker C 24 75645.34",
               ]
        from __builtin__ import float as _float
        d = {}
        for sector,salaries in groupBy(info, key   = lambda rec: rec[2],
                                       value = lambda rec: _float(rec[-1])).iteritems():
            d[sector] = salaries
        self.assertEquals(d, {"C" : [85823.956, 75645.34], "D" : [9694.57]})


if __name__ == '__main__':
    unittest.main()
