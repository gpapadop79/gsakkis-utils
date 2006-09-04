#!/usr/bin/env python

import unittest
from datastructs.immutableseq import ImmutableSequence

__author__ = "George Sakkis <gsakkis@rutgers.edu>"

aSequence = [1,'2',3.0]
anImmutable = ImmutableSequence(aSequence)

class ImmutableSequenceTestSuite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self)
        # standard test suite
        self.addSuite(self._makeTestCase(aSequence, anImmutable))
        # slice test suites
        for slice in iterSlices(aSequence):
            self.addSuite(self._makeTestCase(aSequence[slice],
                                             anImmutable[slice]))
        # slice-of-slice test suites
        aSlice, anImmutableSlice = aSequence[1:-1], anImmutable[1:-1]
        for subslice in iterSlices(aSlice):
            self.addSuite(self._makeTestCase(aSlice[subslice],
                                             anImmutableSlice[subslice]))
        # __add__ test suites
        self.addSuite(self._makeTestCase(aSequence[1:] + aSequence[:-2],
                                         anImmutable[1:] + anImmutable[:-2]))
        # __mul__ test suites
        for n in range(-1,len(aSequence)):
            self.addSuite(self._makeTestCase(aSequence[1:]*n, anImmutable[1:]*n))

    def addSuite(self,testCase):
        self.addTest(unittest.TestLoader().loadTestsFromTestCase(testCase))

    def _makeTestCase(self, sequence, immutable):
        class ATestCase(self.ImmutableSequenceTestCase):
            def setUp(this):
                this.sequence = sequence
                this.immutable = immutable
        return ATestCase


    class ImmutableSequenceTestCase(unittest.TestCase):
        def test_indexing(self):
            size = len(self.sequence)
            for n in xrange(-size,size):
                self.assertEquals(self.sequence[n], self.immutable[n])
            for n in range(-size-5,-size) + range(size,size+5):
                self.assertRaises(IndexError, self.immutable.__getitem__, n)

        def test_len(self):
            self.assertEquals(len(self.immutable), len(self.sequence))

        def test_iter(self):
            it = iter(self.immutable)
            self.assertEquals(list(it), list(self.sequence))
            self.assertRaises(StopIteration, it.next)

        def test_repr(self):
            self.assertEquals(eval(repr(self.immutable)), self.immutable)

        def test_eq(self):
            self.failIf(ImmutableSequence([]))
            self.assertEquals(self.immutable, ImmutableSequence(iter(self.sequence)))
            for cls in tuple,list:
                self.assertNotEquals(self.immutable, cls(self.sequence))

        def test_cmp(self):
            # longer sequence: greater
            self.assert_gt(ImmutableSequence(aSequence + [None]), anImmutable)
            # shorter sequence: smaller
            self.assert_gt(anImmutable, ImmutableSequence(aSequence[:-1]))
            for otherSeq in (
                # same length / greater first item
                [aSequence[0]+1] + aSequence[1:],
                # same length / greater last item
                aSequence[:-1] + [aSequence[-1]+1],
                # same length / greater item before smaller item
                [aSequence[0]+1] + aSequence[1:-1] + [aSequence[-1]-1]):
                self.assert_gt(ImmutableSequence(otherSeq),anImmutable)

        def test_fail(self):
            self.assertRaises(TypeError, self.immutable.__add__, self.sequence)
            self.assertRaises(TypeError, self.sequence.__add__, self.immutable)
            self.assertRaises(TypeError, self.immutable.__mul__, self.immutable)
            for compare in (lambda x,y: x<y,  lambda x,y: x>y,
                            lambda x,y: x<=y, lambda x,y: x>=y):
                self.assertRaises(TypeError, compare, self.immutable, self.sequence)
                self.assertRaises(TypeError, compare, self.sequence, self.immutable)

        def assert_gt(self, x, y):
            self.failUnless(x>y)
            self.failUnless(x>=y)
            self.failUnless(x!=y)
            self.failIf(x==y)
            self.failIf(x<y)
            self.failIf(x<=y)


def iterSlices(sequence, validOnly=True):
    indexes = steps = range(-len(sequence)-1, len(sequence)+2) + [None]
    if validOnly:
        steps = filter(lambda x:x!=0, steps)
    for start in indexes:
        for stop in indexes:
            for step in steps:
                yield slice(start,stop,step)


if __name__ == '__main__':
    unittest.main(defaultTest = "ImmutableSequenceTestSuite")
