#!/usr/bin/env python
#todo: test with __slots__

import unittest
from common.comparable import Comparable
from common.powerset import powerset

__author__ = "George Sakkis <gsakkis@rutgers.edu>"


# A base old-style class without rich comparators
class BaseOldClass:
    def __init__(self,x): self._x = x

# A base new-style class without rich comparators
class BaseNewClass(BaseOldClass,object):
    pass

# comparator functions to be added dynamically to subclasses of BaseClass
def __eq__(self,other):
    try: return int(self._x) == int(other._x)
    except: return False
def __ne__(self,other):
    try: return int(self._x) != int(other._x)
    except: return True
def __gt__(self,other):
    return int(self._x) > int(other._x)
def __ge__(self,other): return int(self._x) >= int(other._x)
def __lt__(self,other): return int(self._x) < int(other._x)
def __le__(self,other): return int(self._x) <= int(other._x)
def __cmp__(self,other): return cmp(int(self._x, self._y))


class ComparableTestSuite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self)
        for base in BaseNewClass, BaseOldClass:
            # identity test suite
            self.addSuite(ComparableTestCase_id, base)
            # greater-than et al. suites
            for comparators in powerset([__gt__, __lt__, __ge__, __le__]):
                if comparators:
                    baseUnitTest = ComparableTestCase_all
                    # TypeError: undefined both __eq__ and __ne__
                    try: self.addSuite(baseUnitTest, base, *comparators)
                    except TypeError: pass
                    else: raise AssertionError
                else:
                    baseUnitTest = ComparableTestCase_eq_ne
                self.addSuite(baseUnitTest, base, __eq__, *comparators)
                self.addSuite(baseUnitTest, base, __ne__, *comparators)
                self.addSuite(baseUnitTest, base, __eq__, __ne__, *comparators)

    def addSuite(self, baseUnitTest, base, *functions):
        # Add comparator operators (using Comparable) to a subclass of base
        name = "%s_%s" % (base.__name__, '_'.join([f.__name__
                                                   for f in functions]))
        mixin_ops = dict([(f.__name__,f) for f in functions])
        cls = Comparable(name, (base,), mixin_ops)
        class ATestCase(baseUnitTest):
            def setUp(this):
                this.x1 = cls("0")
                this.x2 = cls(0.0)
                this.y = cls(1)
                this.z = cls(None)
            def testComparators(this):
                # assert that the existing comparators were not replaced
                for f in functions:
                    this.failUnless(getattr(cls,f.__name__).im_func is f)
                # assert that the implied missing comparators were added
                # 1. if at least one of __eq__, __ne__ were defined,
                # both of them are implied
                if '__eq__' in mixin_ops or '__ne__' in mixin_ops:
                    this.failUnless(hasattr(cls, '__eq__')
                                    and hasattr(cls, '__ne__'))
                # 2. if at least one of __gt__, __lt__, __ge__, __le__ were
                # defined, all of them are implied
                mixin_op_names = mixin_ops.keys()
                if ('__gt__' in mixin_op_names or '__lt__' in mixin_op_names
                    or '__ge__' in mixin_op_names or '__le__' in mixin_op_names):
                    this.failUnless(hasattr(cls, '__gt__')
                                    and hasattr(cls, '__lt__')
                                    and hasattr(cls, '__ge__')
                                    and hasattr(cls, '__le__'))
        self.addTest(unittest.TestLoader().loadTestsFromTestCase(ATestCase))


class ComparableTestCase(unittest.TestCase):
    def test_eq(self):
        self.failUnless(self.x1 == self.x1)
        self.failIf(self.x1 == self.y)
        self.failIf(self.x1 == self.z)
        self.failIf(self.x1 == 0)
    def test_ne(self):
        self.failIf(self.x1 != self.x1)
        self.failUnless(self.x1 != self.y)
        self.failUnless(self.x1 != self.z)
        self.failUnless(self.x1 != 0)


class ComparableTestCase_id(ComparableTestCase):
    def test_eq(self):
        super(ComparableTestCase_id,self).test_eq()
        self.failIf(self.x1 == self.x2)
        self.failIf(self.x2 == self.x1)
    def test_ne(self):
        super(ComparableTestCase_id,self).test_ne()
        self.failUnless(self.x1 != self.x2)
        self.failUnless(self.x2 != self.x1)


class ComparableTestCase_eq_ne(ComparableTestCase):
    def test_eq(self):
        super(ComparableTestCase_eq_ne,self).test_eq()
        self.failUnless(self.x1 == self.x2)
        self.failUnless(self.x2 == self.x1)
    def test_ne(self):
        super(ComparableTestCase_eq_ne,self).test_ne()
        self.failIf(self.x1 != self.x2)
        self.failIf(self.x2 != self.x1)


class ComparableTestCase_all(ComparableTestCase):
    def test_gt(self):
        for x in self.x1, self.x2:
            self.failUnless(self.y > x)
            self.failIf(x > self.y)
        self.failIf(self.x1 > self.x2)
        self.failIf(self.x2 > self.x1)
        for x in self.x1, self.x2, self.y:
            self.assertRaises(Exception, lambda a,b:a>b, x, self.z)
            self.assertRaises(Exception, lambda a,b:a>b, self.z, x)
    def test_lt(self):
        for x in self.x1, self.x2:
            self.failUnless(x < self.y)
            self.failIf(self.y < x)
        self.failIf(self.x1 < self.x2)
        self.failIf(self.x2 < self.x1)
        for x in self.x1, self.x2, self.y:
            self.assertRaises(Exception, lambda a,b:a<b, x, self.z)
            self.assertRaises(Exception, lambda a,b:a<b, self.z, x)
    def test_ge(self):
        for x in self.x1, self.x2:
            self.failUnless(self.y >= x)
            self.failIf(x >= self.y)
        self.failUnless(self.x1 >= self.x2)
        self.failUnless(self.x2 >= self.x1)
        for x in self.x1, self.x2, self.y:
            for pair in (x,self.z), (self.z,x):
                self.assertRaises(Exception, lambda a,b:a>=b, *pair)
    def test_le(self):
        for x in self.x1, self.x2:
            self.failUnless(x <= self.y)
            self.failIf(self.y <= x)
        self.failUnless(self.x1 <= self.x2)
        self.failUnless(self.x2 <= self.x1)
        for x in self.x1, self.x2, self.y:
            for pair in (x,self.z), (self.z,x):
                self.assertRaises(Exception, lambda a,b:a>=b, *pair)


def getComparators(obj):
    '''Return the names of the comparator methods defined for this object.'''
    return [getattr(obj,method) for method in
            ["__%s__" % op for op in 'eq ne gt lt le ge cmp'.split()]
            if hasattr(obj,method)]

if __name__ == '__main__':
    unittest.main(defaultTest = "ComparableTestSuite")
