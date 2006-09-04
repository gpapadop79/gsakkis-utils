#!/usr/bin/env python

import unittest
from common.abstract import *

__author__ = "George Sakkis <gsakkis@rutgers.edu>"


class AbstractTestCase(unittest.TestCase):
    def test_NotImplemented(self):

        class SomeBase(dict):
            needed = also_needed = NotImplemented
        SomeBase = abstractclass(SomeBase)

        class Derived(SomeBase):
            def needed(self): return 3

        class Further(Derived):
            def also_needed(self): return 1

        self.assertRaises(NotImplementedError,SomeBase)
        self.assertRaises(NotImplementedError,Derived)
        Further() # works

    def test_abstractmethod(self):
        class SomethingMissing(object):
            # @abstractmethod
            def function(self):
                '''Implement me'''
            function = abstractmethod(function)

        class UsesMissing(SomethingMissing):
            pass
        UsesMissing = abstractclass(UsesMissing)

        class Override(UsesMissing):
            def function(self):
                return 23

        SomethingMissing() # works
        self.assertRaises(NotImplementedError,UsesMissing)
        Override() # works

    def test_no_abstractmethod(self):
        class SomeBase(object):
            # This class has no abstract methods; yet calling foo() or bar()
            # on an instance of this class would cause infinite recursion.
            # Hence it is defined as abstract, and its concrete subclasses
            # should override at least one of (foo,bar) in a way that breaks
            # the recursion.
            def __init__(self, x):
                self._x = x
            def foo(self, y):
                return self.bar(self._x + y)
            def bar(self, y):
                return self.foo(self._x - y)
        SomeBase = abstractclass(SomeBase)

        class Derived(SomeBase):
            def __init__(self,x):
                SomeBase.__init__(self,x)
            def foo(self,y):
                return self._x * y

        self.assertRaises(NotImplementedError,SomeBase,3)
        self.assertEquals(Derived(5).bar(2), 15)

    def test_meta(self):
        for metaclass in type,AbstractCheckMeta:
            class SomeBase(object):
                __metaclass__ = metaclass
                def __init__(self, x):
                    self._x = x
                # @abstractmethod
                def foo(self): '''Abstract method.'''
                foo = abstractmethod(foo)
            SomeBase = abstractclass(SomeBase)

            class Derived(SomeBase):
                pass

            self.assertRaises(NotImplementedError,SomeBase,3)
            self.assertRaises(NotImplementedError,Derived,3)

    def test_wrongmeta(self):
        class OtherMeta(type): pass
        class SomeBase(object):
            __metaclass__ = OtherMeta
            def __init__(self, x):
                self._x = x
            # @abstractmethod
            def foo(self): '''Abstract method.'''
            foo = abstractmethod(foo)
        self.assertRaises(TypeError,abstractclass,SomeBase)

    def test_existing_abstractmethods(self):
        class SomeBase(object):
            __abstractmethods__ = []
        self.assertRaises(TypeError,abstractclass,SomeBase)


if __name__ == '__main__':
    unittest.main()
