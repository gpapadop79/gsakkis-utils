#!/usr/bin/env python

import unittest
from datastructs.memo import *

__author__ = "George Sakkis <gsakkis@rutgers.edu>"


class MemoTestCase(unittest.TestCase):
    def test_Memoize(self):
        foo = self._aFunction()
        memfoo = Memoize(foo)
        for i in range(3):
            self.assertEquals(foo(1,2), memfoo(1,2))
            self.assertEquals(foo(1,2,3), memfoo(1,2,3))
            self.assertEquals(foo(1,2,3,4), memfoo(1,2,3,4))
            self.assertEquals(foo(1,2,3,4,5), memfoo(1,2,3,4,5))
            self.assertEquals(foo(1,2,z="6"), memfoo(1,2,z="6"))
            self.assertEquals(foo(1,2,3,4,z="6"), memfoo(1,2,3,4,z="6"))
            self.assertEquals(foo(1,2,3,4,5,z="6"), memfoo(1,2,3,4,5,z="6"))

    def test_memoizedmethod(self):
        foo = self._aFunction()
        class C:
            def __init__(self,x,y):
                # self._x, self._y should not be changed after initialization
                self._x = x; self._y = y
                self.memfoo1 = Memoize(self.foo)

            def foo(self,alpha,beta):
                return foo(self._x,self._y,alpha,beta)

            memfoo2 = memoizedmethod(foo)

        class Csub(C):
            memfoo3 = memoizedmethod(C.foo)

        c = Csub(1,2)
        memfoos = [getattr(c,name) for name in 'memfoo1','memfoo2','memfoo3']
        args = 3,4
        for i in range(10):
            v = c.foo(*args)
            for memfoo in memfoos:
                self.assertEquals(v, memfoo(*args))
        # if the state of the object changes, the memoized methods may return
        # wrong results
        c._x *= 2
        for i in range(10):
            v = c.foo(*args)
            for memfoo in memfoos:
                self.assertEquals(memfoos[0](*args), memfoo(*args))
            for memfoo in memfoos:
                self.assertNotEquals(v, memfoo(*args))

    def test_Memento(self):
        class Foo:
            __metaclass__ = Memento
            def __init__(self, arg1, arg2=None, *args, **kwds):
                pass

        class Bar(Foo):
            def __init__(self, arg1, arg2=None, *args, **kwds):
                Foo.__init__(self, arg1, arg2, *args, **kwds)

        for cls in Foo,Bar:
            self.assertSame(cls(1), cls(1))
            self.assertSame(cls(1,2), cls(1,2))
            self.assertSame(cls(1,2,3), cls(1,2,3))
            self.assertSame(cls(1,x="4"), cls(1,x="4"))
            self.assertSame(cls(1,2,3,x="4"), cls(1,2,3,x="4"))

        self.assertNotSame(Foo(1), Bar(1))
        self.assertNotSame(Foo(1,2), Bar(1,2))
        self.assertNotSame(Foo(1,2,3), Bar(1,2,3))
        self.assertNotSame(Foo(1,x="4"), Bar(1,x="4"))
        self.assertNotSame(Foo(1,2,3,x="4"), Bar(1,2,3,x="4"))

    def assertSame(self,x,y):
        self.assertEquals(id(x), id(y))

    def assertNotSame(self,x,y):
        self.assertNotEquals(id(x), id(y))

    def _aFunction(self):
        from math import sqrt,log,sin,cos
        def computeSomething(x,y,alpha=1,beta=2, *args, **kwds):
            w = log(alpha) * sqrt(x * alpha + y * beta)
            z = log(beta) * sqrt(x * beta + y * alpha)
            return sin(z) / cos(w), args, kwds
        return computeSomething


if __name__ == '__main__':
    unittest.main()
