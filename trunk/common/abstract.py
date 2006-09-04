'''Support for abstract methods and classes.

In most cases, only L{abstractclass} needs to be imported from this module to
specify a class as abstract. A method is specified as abstract either by being
decorated by the L{abstractmethod} decorator or simply by being assigned to
NotImplemented.

The L{AbstractCheckMeta} metaclass is necessary only when it conflicts with
the metaclass of a class C to be cast as abstract. In this case, the conflict
has to be resolved by multiply inheriting from the two metaclasses and setting
the new metaclass as the __metaclass__ of C.

History:
    - First sketch by Alex Martelli.
    - First working implementation by John Machin.
    - Current implementation by George Sakkis.
'''


import inspect

__all__ = ["abstractclass", "abstractmethod", "AbstractCheckMeta"]


def abstractclass(cls):
    '''Make a class abstract.

    Example::
        # hopefully class decorators will be supported in python 2.x
        # for some x, x>4
        #@abstractclass
        class SomeBase(object):
            @abstractmethod
            def function(self):
                """Implement me"""
        # the only way as of python 2.4
        SomeBase = abstractclass(SomeBase)

    @param cls: A new-style class object.
    @return: A surrogate of C{cls} that behaves as abstract. The returned
        class raises NotImplementedError if attempted to be instantiated
        directly; still its subclasses may call its __init__. A subclass of
        the returned class is also abstract if it has one or more abstract
        methods, or if it is also explicitly decorated by this function. A
        method is declared abstract by being assigned to NotImplemented (or
        decorated by L{abstractmethod}).
    @raise TypeError: If there is a metaclass conflict between C{type(cls)}
        and L{AbstractCheckMeta}, or if C{cls} has an C{__abstractmethods__}
        attribute.
    '''
    # check if cls has AbstractCheckMeta (or a subtype) for metaclass
    metaclass = type(cls)
    if not issubclass(metaclass, AbstractCheckMeta):
        # it doesn't; try to make AbstractCheckMeta its metaclass by
        # inheriting from _AbstractCheck
        cls = metaclass(cls.__name__, (_AbstractCheck,) + cls.__bases__,
                        dict(cls.__dict__))
    # replace __init__ with a proxy ensuring that __init__ is called by a
    # subclass (but not directly)
    old_init = getattr(cls,'__init__',None)
    def new_init(self,*args,**kwds):
        if self.__class__ is cls:
            raise NotImplementedError("%s is an abstract class" % cls.__name__)
        if old_init is not None:
            old_init(self,*args,**kwds)
    cls.__init__ = new_init
    return cls


def abstractmethod(function):
    '''A method decorator for those who prefer the parameters declared.'''
    return NotImplemented


class AbstractCheckMeta(type):
    '''A metaclass to detect instantiation of abstract classes.'''

    def __init__(cls, name, bases, dict):
        if '__abstractmethods__' in cls.__dict__:
            raise TypeError("'__abstractmethods__' is already defined in "
                            "class '%s': %s" % (cls.__name__,
                            cls.__dict__['__abstractmethods__']))
        type.__init__(cls, name, bases, dict)
        cls.__abstractmethods__ = [name for name, value in
                                   inspect.getmembers(cls)
                                   if value is NotImplemented]

    def __call__(cls, *args, **kwargs):
        if cls.__abstractmethods__:
            raise NotImplementedError(
                "Class '%s' cannot be instantiated: Methods %s are abstract."
                % (cls.__name__,", ".join(map(repr,cls.__abstractmethods__))))
        return type.__call__(cls, *args, **kwargs)


class _AbstractCheck(object):
    '''
    A class to stick anywhere in an inheritance chain to make its
    descendants being checked for whether they are abstract.
    '''
    __metaclass__ = AbstractCheckMeta
