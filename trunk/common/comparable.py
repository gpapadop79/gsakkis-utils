__author__ = "George Sakkis <gsakkis@rutgers.edu>"
__all__ =  ["Comparable"]

class Comparable(type):
    '''Metaclass for adding automagically "rich comparison" methods to a class.

    The metaclass adds automatically C{__ne__} (resp. C{__eq__}) if C{__eq__}
    (resp. C{__ne__}) is defined and C{__ne__} (resp. C{__eq__}) is not.
    Additionally, if the class defines one or more of C{__gt__}, C{__ge__},
    C{__lt__}, C{__le__}, the rest are also added by this metaclass so that
    the implied relationships among the comparison operators hold.

    The rich comparison methods defined in a class are expected to have the
    following properties:
        - C{__gt__}, C{__ge__}, C{__lt__}, C{__le__} may raise an Exception,
        but C{__eq__} and C{__ne__} may not.
        - If one of the operators raises an Exception, then calling C{__eq__}
        with the same arguments should return False and calling C{__ne__}
        should return True.
    '''

    def __new__(meta, name, bases, classdict):
        # accomodate old-style classes as well
        if not filter(lambda base: issubclass(base,object), bases):
            bases += (object,)
        return super(Comparable, meta).__new__(meta, name, bases, classdict)

    def __init__(cls, name, bases, classdict):
        super(Comparable, cls).__init__(name, bases, classdict)
        def setIfUnset(attr,value):
            if not hasattr(cls,attr): setattr(cls,attr,value)
        if hasattr(cls,'__ne__'):
            setIfUnset('__eq__', lambda self,other: not self != other)
            if hasattr(cls,'__gt__'):
                setIfUnset('__le__', lambda self,other: not self>other)
                setIfUnset('__ge__',
                            lambda self,other: self>other or not self!=other)
                setIfUnset('__lt__',
                            lambda self,other: not self>other and self!=other)
            elif hasattr(cls,'__lt__'):
                setIfUnset('__ge__', lambda self,other: not self<other)
                setIfUnset('__gt__',
                            lambda self,other: not self<other and self!=other)
                setIfUnset('__le__',
                            lambda self,other: self<other or not self!=other)
            elif hasattr(cls,'__ge__'):
                setIfUnset('__lt__', lambda self,other: not self>=other)
                setIfUnset('__gt__',
                            lambda self,other: self>=other and self!=other)
                setIfUnset('__le__',
                            lambda self,other: not (self>=other and self!=other))
            elif hasattr(cls,'__le__'):
                setIfUnset('__gt__', lambda self,other: not self<=other)
                setIfUnset('__ge__',
                            lambda self,other: not (self<=other and self!=other))
                setIfUnset('__lt__',
                            lambda self,other: self<=other and self!=other)
        elif hasattr(cls,'__eq__'):
            setIfUnset('__ne__', lambda self,other: not self == other)
            if hasattr(cls,'__gt__'):
                setIfUnset('__le__', lambda self,other: not self>other)
                setIfUnset('__ge__',
                            lambda self,other: self>other or self==other)
                setIfUnset('__lt__',
                            lambda self,other: not (self>other or self==other))
            elif hasattr(cls,'__lt__'):
                setIfUnset('__ge__', lambda self,other: not self<other)
                setIfUnset('__gt__',
                            lambda self,other: not (self<other or self==other))
                setIfUnset('__le__',
                            lambda self,other: self<other or self==other)
            elif hasattr(cls,'__ge__'):
                setIfUnset('__lt__', lambda self,other: not self>=other)
                setIfUnset('__gt__',
                            lambda self,other: self>=other and not self==other)
                setIfUnset('__le__',
                            lambda self,other: not self>=other or self==other)
            elif hasattr(cls,'__le__'):
                setIfUnset('__gt__', lambda self,other: not self<=other)
                setIfUnset('__ge__',
                            lambda self,other: not self<=other or self==other)
                setIfUnset('__lt__',
                            lambda self,other: self<=other and not self==other)
        elif (hasattr(cls,'__gt__') or hasattr(cls,'__lt__')
              or hasattr(cls,'__ge__') or hasattr(cls,'__le__')):
            raise TypeError("Potentially incosistent comparable; define __eq__"
                            " or __ne__ in class '%s'" % cls.__name__)
