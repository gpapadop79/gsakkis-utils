#!/usr/bin/env python

import sys
import inspect
import unittest

from common.typecheck import *
from common.typecheck import _TypeCheckedFunction

__author__ = "George Sakkis <gsakkis@rutgers.edu>"


class TypeCheckedFunctionTestCase(unittest.TestCase):

    def test_getParamsDict_0(self):
        def f(a):
            return inspect.getargvalues(sys._getframe())[-1]
        getParams = _TypeCheckedFunction(f)._getParamsDict
        self.assertEquals(f(0),     getParams(0))
        self.assertEquals(f(a=0),   getParams(a=0))
        self.assertRaises(TypeError, getParams)
        self.assertRaises(TypeError, getParams, 1, 2)
        self.assertRaises(TypeError, getParams, x=2)

    def test_getParamsDict_1(self):
        def f(a, b=-1):
            return inspect.getargvalues(sys._getframe())[-1]
        getParams = _TypeCheckedFunction(f)._getParamsDict
        self.assertEquals(f(0),         getParams(0))
        self.assertEquals(f(a=0),       getParams(a=0))
        self.assertEquals(f(0,1),       getParams(0,1))
        self.assertEquals(f(0,b=1),     getParams(0,b=1))
        self.assertEquals(f(b=1,a=0),   getParams(b=1,a=0))
        self.assertRaises(TypeError, getParams)
        self.assertRaises(TypeError, getParams, x=2)
        self.assertRaises(TypeError, getParams, 1, 2, 3)
        self.assertRaises(TypeError, getParams, b=2)
        self.assertRaises(TypeError, getParams, 3, a=3)
        self.assertRaises(TypeError, getParams, 3, x=3)

    def test_getParamsDict_2(self):
        def f(a, b=-1, *f_args):
            return inspect.getargvalues(sys._getframe())[-1]
        getParams = _TypeCheckedFunction(f)._getParamsDict
        self.assertEquals(f(0),         getParams(0))
        self.assertEquals(f(a=0),       getParams(a=0))
        self.assertEquals(f(0,1),       getParams(0,1))
        self.assertEquals(f(0,b=1),     getParams(0,b=1))
        self.assertEquals(f(b=1,a=0),   getParams(b=1,a=0))
        self.assertEquals(f(0,1,2),     getParams(0,1,2))
        self.assertRaises(TypeError, getParams)
        self.assertRaises(TypeError, getParams, x=2)
        self.assertRaises(TypeError, getParams, b=2)
        self.assertRaises(TypeError, getParams, 3, a=3)
        self.assertRaises(TypeError, getParams, 3, x=3)
        self.assertRaises(TypeError, getParams, 1, 2, b=2)
        self.assertRaises(TypeError, getParams, 1, 2, 3, b=2)

    def test_getParamsDict_3(self):
        def f(a, b=-1, **f_kwds):
            return inspect.getargvalues(sys._getframe())[-1]
        getParams = _TypeCheckedFunction(f)._getParamsDict
        self.assertEquals(f(0),         getParams(0))
        self.assertEquals(f(a=0),       getParams(a=0))
        self.assertEquals(f(0,1),       getParams(0,1))
        self.assertEquals(f(0,b=1),     getParams(0,b=1))
        self.assertEquals(f(b=1,a=0),   getParams(b=1,a=0))
        self.assertEquals(f(0,1,x=2),   getParams(0,1,x=2))
        self.assertEquals(f(0,x=2),     getParams(0,x=2))
        self.assertEquals(f(x=2,a=0),   getParams(x=2,a=0))
        self.assertRaises(TypeError, getParams)
        self.assertRaises(TypeError, getParams, x=2)
        self.assertRaises(TypeError, getParams, b=2)
        self.assertRaises(TypeError, getParams, 3, a=3)
        self.assertRaises(TypeError, getParams, 1, 2, b=2)
        self.assertRaises(TypeError, getParams, 1, 2, 3, b=2)
        self.assertRaises(TypeError, getParams, 1, 2, 3)
        self.assertRaises(TypeError, getParams, b=2, x=3)

    def test_getParamsDict_4(self):
        def f(a, b=-1, *f_args, **f_kwds):
            return inspect.getargvalues(sys._getframe())[-1]
        getParams = _TypeCheckedFunction(f)._getParamsDict
        self.assertEquals(f(0),         getParams(0))
        self.assertEquals(f(a=0),       getParams(a=0))
        self.assertEquals(f(0,1),       getParams(0,1))
        self.assertEquals(f(0,b=1),     getParams(0,b=1))
        self.assertEquals(f(b=1,a=0),   getParams(b=1,a=0))
        self.assertEquals(f(0,1,x=2),   getParams(0,1,x=2))
        self.assertEquals(f(0,x=2),     getParams(0,x=2))
        self.assertEquals(f(x=2,a=0),   getParams(x=2,a=0))
        self.assertEquals(f(0,1,2),     getParams(0,1,2))
        self.assertEquals(f(0,1,2,x=3), getParams(0,1,2,x=3))
        self.assertRaises(TypeError, getParams)
        self.assertRaises(TypeError, getParams, x=2)
        self.assertRaises(TypeError, getParams, b=2)
        self.assertRaises(TypeError, getParams, 3, a=3)
        self.assertRaises(TypeError, getParams, 1, 2, b=2)
        self.assertRaises(TypeError, getParams, 1, 2, 3, b=2)
        self.assertRaises(TypeError, getParams, b=2, x=3)


class C: pass
class Csub(C): pass
class N(object): pass
class Nsub(N): pass


class TypeChecksTestCase(unittest.TestCase):

    def test_instanceOf(self):
        import types
        instanceOf(int)(3)
        instanceOf(list)([])
        self.assertRaises(TypeError, instanceOf(int), 3.0)
        for cls,cls_sub in (C,Csub),(N,Nsub):
            instanceOf(cls)(cls())
            instanceOf(cls)(cls_sub())
            self.assertRaises(TypeError, instanceOf(cls_sub), cls())
        for cls in C,Csub:
            instanceOf(types.ClassType)(cls)
        for cls in N,Nsub:
            instanceOf(type)(cls)

    def test_typeIs(self):
        typeIs(int)(3)
        typeIs(list)([])
        for cls,cls_sub in (C,Csub),(N,Nsub):
            typeIs(cls)(cls())
            self.assertRaises(TypeError, typeIs(cls), cls_sub())

    def test_ContainerOf(self):
        containers = [list,tuple]
        try:
            from sets import Set,ImmutableSet
            containers += [Set,ImmutableSet]
        except ImportError: pass
        for container in containers:
            for cls,cls_sub in (C,Csub),(N,Nsub):
                # size=None tests
                check = containerOf(cls)
                check(container([cls(), cls_sub()]))
                check(container([cls()]))
                check(container())
                self.assertRaises(TypeError, check, cls())
                self.assertRaises(TypeError, check, container([cls(),"foo"]))
                # size != None
                check = containerOf(cls, size=2)
                check(container([cls(), cls_sub()]))
                self.assertRaises(TypeError, check, container([cls()]))
                check = containerOf(cls, size=lambda n: n%2==1 and n>1)
                check(container([cls(),cls(),cls()]))
                self.assertRaises(TypeError, check, container([cls(),cls(),
                                                               cls(),cls()]))
                self.assertRaises(TypeError, check, container([cls(),cls()]))
                self.assertRaises(TypeError, check, container([cls()]))

    def test_RecordOf(self):
        for container in list,tuple:
            check = recordOf(C,N,int)
            check(container([C(), Nsub(), 1]))
            check(container([Csub(), N(), 1]))
            self.assertRaises(TypeError, check, container([C(), N()]))
            self.assertRaises(TypeError, check, container([1, C(), N()]))
            check = recordOf(float)
            check(container([3.12]))
            self.assertRaises(TypeError, check, 3.12)

    def test_ListOf(self):
        for cls,cls_sub in (C,Csub),(N,Nsub):
            check = listOf(cls)
            check([cls(), cls_sub()])
            check([cls()])
            check([])
            self.assertRaises(TypeError, check, cls())
            self.assertRaises(TypeError, check, (cls(),cls_sub()))
            self.assertRaises(TypeError, check, [cls(),"foo"])

    def test_TupleOf(self):
        for cls,cls_sub in (C,Csub),(N,Nsub):
            check = tupleOf(cls)
            check((cls(), cls_sub()))
            check((cls(),))
            check(())
            self.assertRaises(TypeError, check, cls())
            self.assertRaises(TypeError, check, [cls(),cls_sub()])
            self.assertRaises(TypeError, check, (cls(),"foo"))

    def test_SetOf(self):
        from sets import Set,ImmutableSet
        for set in Set, ImmutableSet:
            for cls,cls_sub in (C,Csub),(N,Nsub):
                check = setOf(cls)
                check(set([cls(), cls_sub()]))
                check(set([cls()]))
                check(set())
                self.assertRaises(TypeError, check, cls())
                self.assertRaises(TypeError, check, [cls(),cls()])
                self.assertRaises(TypeError, check, set([cls(),"foo"]))

    def test_MappingOf(self):
        from UserDict import UserDict
        for map in dict,UserDict:
            for cls,cls_sub in (C,Csub),(N,Nsub):
                check = mappingOf(key=cls)
                check(map({cls_sub() : 1}))
                check(map())
                self.assertRaises(TypeError, check, map({1 : cls()}))
                check = mappingOf(value=cls)
                check(map({1 : cls_sub()}))
                check(map())
                self.assertRaises(TypeError, check, map({cls() : 1}))
                check = mappingOf(cls,cls_sub)
                check(map({cls_sub() : cls_sub()}))
                check(map())
                self.assertRaises(TypeError, check, map({cls() : cls()}))

    def test_DictOf(self):
        from UserDict import UserDict
        for cls,cls_sub in (C,Csub),(N,Nsub):
            check = dictOf(key=cls)
            check({cls_sub() : 1})
            check({})
            self.assertRaises(TypeError, check, {1 : cls()})
            self.assertRaises(TypeError, check, UserDict())
            check = dictOf(value=cls)
            check({1 : cls_sub()})
            check({})
            self.assertRaises(TypeError, check, {cls() : 1})
            self.assertRaises(TypeError, check, UserDict())
            check = dictOf(cls,cls_sub)
            check({cls_sub() : cls_sub()})
            check({})
            self.assertRaises(TypeError, check, {cls() : cls()})
            self.assertRaises(TypeError, check, UserDict())

    def test_and(self):
        class CN(C,N): pass
        class CNsub(Csub,Nsub): pass
        check = instanceOf(C) & instanceOf(N)
        for cls in CN,CNsub:
            check(cls())
        for cls in C,Csub,N,Nsub:
            self.assertRaises(TypeError, check, cls())
        for c1,c2 in (C,N),(N,C):
            # allow either of two operands to be type or class
            for check in (c1 & instanceOf(c2), instanceOf(c2) & c1):
                for cls in CN,CNsub:
                    check(cls())
                for cls in C,Csub,N,Nsub:
                    self.assertRaises(TypeError, check, cls())

    def test_or(self):
        check = instanceOf(Csub) | instanceOf(Nsub)
        for cls in Csub,Nsub:
            check(cls())
        for cls in C,N:
            self.assertRaises(TypeError, check, cls())
        for c1,c2 in (C,N),(N,C):
            # allow either of two operands to be type or class
            for check in (c1 | instanceOf(c2), instanceOf(c2) | c1):
                check(c1()); check(c2())

    def test_typecheck(self):
        def foo(x):
            d=len(x)
            # by default use the caller's locals()
            typecheck(x=str,d=int)
            # pass explicitly the environment to check
            vars = sys._getframe(1).f_locals
            typecheck(vars, z=float)
            # unknown variables are caught
            self.assertRaises(ValueError, typecheck, z=float)
            self.assertRaises(ValueError, typecheck, vars, x=str)
        self.assertRaises(TypeError, foo, 3)
        # foo expects z to be float
        z=3.0; foo("")
        # don't call self.assertRaises so that it is not added to the call stack
        # instead simulate assertRaises in this scope
        try: z="str"; foo("")
        except TypeError: pass
        else: self.assert_(False)

    def test_expects(self):
        class Child: pass
        class Phone(object): pass
        checkedParams = {
            "name"      : tupleOf(str,size=2),
            "birthday"  : recordOf(int,str,int),
            "height"    : float,
            "children"  : listOf(Child),
            "phonebook" : dictOf(str,containerOf(Phone))
        }
        def foo(name,birthday,height,children,phonebook,extra):
            pass
        foo_argcheck = expects(**checkedParams)(foo)
        # real arguments with correct types
        realArgs = {
            "name"      : ("Paul","Smith"),
            "birthday"  : (12,"March", 1978),
            "height"    : 1.84,
            "children"  : [Child(),Child()],
            "phonebook" : { "Mike"   : (Phone(),Phone()),
                            "office" : [Phone()]},
            "extra"     : None}
        # closure for trying correct calls
        def test_pass(**args):
            copy = dict(realArgs)
            copy.update(args)
            foo_argcheck(**copy)
        # closure for trying maltyped calls
        def test_fail(**args):
            copy = dict(realArgs)
            copy.update(args)
            self.assertRaises(TypeError, foo_argcheck, **copy)
        test_pass()
        test_pass(children=[])
        test_pass(phonebook={"Jim": []})
        test_fail(name="Paul Smith")
        test_fail(name="Paul Smith".split())
        test_fail(birthday=(12,3,1978))
        test_fail(children=Child())
        test_fail(children=[Child(),"john"])
        test_fail(phonebook={"Jim": [1234567]})
        # unknown typical arguments ('dummy') are detected at declaration time
        self.assertRaises(ValueError, expects(dummy=int), foo)

    def test_returnType(self):
        import types
        def foo(x):
            if x: return [x]
            else: return None
        foo = returns(types.NoneType | listOf(int))(foo)
        for arg in 0,"",1:
            foo(arg)
        self.assertRaises(TypeError, foo, "1")

if __name__ == '__main__':
    unittest.main()
