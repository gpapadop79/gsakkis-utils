def innerclass(cls):
    '''Class decorator for making a class behave as a Java inner class.'''
    return _InnerClassDescriptor(cls,False)

def nestedclass(cls):
    '''Class decorator for making a class behave as a Java static inner (aka
    nested) class.'''
    return _InnerClassDescriptor(cls,True)

class _InnerClassDescriptor(object):
    '''Wraps an inner class so that it is associated with its enclosing class
    (for static inner class) or an instance of its enclosing class (for
    non-static nested class).

    The outer object (either class or instance) is referenced implicitly when
    an attribute lookup fails in the inner object's scope. It can also be
    referenced explicitly through the attribute 'this' of the inner instance.
    '''
    def __init__(self, cls, isStatic):
        self._inner = cls
        self._isStatic = isStatic
        if hasattr(cls,'this'):
            raise TypeError("Cannot set attribute 'this' in inner class")

    def __get__(self,outer,outercls):
        if self._isStatic:
        # for static nested classes, the outer object is the enclosing class
            outer = outercls
        innercls = self._inner
        clsdict = innercls.__dict__.copy()
        def getOuter(self,attr):
            try: return getattr(outer,attr)
            except AttributeError:
                outername = "%s.%s.%s" %(outercls.__module__,
                                        outercls.__name__, innercls.__name__)
                if outer is not None:
                    raise AttributeError("Class %s has no attribute %r" %
                                          (outername,attr))
                raise AttributeError("Static nested class %s cannot access "
                                "non-static attribute %r" % (outername,attr))
        # getOuter is called if the attribute is not found in the inner class
        # scope
        clsdict['__getattr__'] = getOuter
        # explicit read-only reference the outer object
        clsdict['this'] = property(lambda self: outer)
        return type(innercls.__name__, innercls.__bases__, clsdict)


def testInner():
    class Outer:
        def __init__(self,x):
            self.x = x

        #if python gets class decorators, this will be the prefered idiom:
        #@innerclass
        class Inner:
            def __init__(self, y):
                self.y=y
            def sum(self):
                return self.x + self.y
        # the only way as of python 2.4
        Inner = innerclass(Inner)

    outer = Outer(1); inner = outer.Inner(2)
    assert inner.sum() == 3
    outer.x=4; assert inner.sum() == 6
    # creates new x in inner
    inner.x=10; assert inner.sum() == 12
    # outer.x has been shadowed
    assert inner.x == 10
    outer.x=0; assert inner.sum() == 12
    # the outer instance can still be reference explicitly by 'this'
    assert inner.this.x == outer.x == 0
    # a (non-static) inner class must be bounded to an outer class instance
    try: Outer.Inner(2).sum()
    except AttributeError: pass
    else: assert False


def testNested():
    class Outer:
        x="a"

        #@nestedclass
        class Nested:
            def __init__(self, y):
                self.y=y
            def sum(self):
                return self.x + self.y
        Nested = nestedclass(Nested)

    nested = Outer.Nested("b")
    assert nested.sum() == "ab"
    Outer.x = "c"; assert nested.sum() == "cb"
    # outer.x has been shadowed
    nested.x = "d"; assert nested.sum() == "db"
    # the outer instance can still be reference explicitly by 'this'
    assert nested.this.x == Outer.x == 'c'


if __name__ == '__main__':
    testInner()
    testNested()
