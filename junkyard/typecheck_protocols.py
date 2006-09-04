'''Module for supporting strict runtime type checking.

@sort: TypeCheck, instanceOf, typeIs, containerOf, recordOf, mappingOf,
       tupleOf, listOf, setOf, dictOf
@group Enforcing The Type Checks: typecheck, params, returns
'''

try: from itertools import izip
except ImportError: izip = zip

import types
from protocols import AbstractBase, adapt, advise
#, Interface, declareAdapter, Protocol


__author__ = "George Sakkis <gsakkis@rutgers.edu>"

__all__ = '''TypeCheck instanceOf typeIs containerOf recordOf mappingOf
             tupleOf listOf setOf dictOf typecheck params returns
          '''.split()


#======= Type check definitions ==============================================

class TypeCheck(AbstractBase):
    '''Abstract base class for runtime type checks.

    A TypeCheck is a callable instance that given an object either accepts it
    and returns silently or raises TypeError. The exact definition of a "type"
    is left for the concrete subclasses; thus a "type" can be more general
    than a regular python type or class. For example, "types" such as "list of
    integers", "dictionary with string keys and tuples of float values", etc.
    can be defined and validated at runtime.

    @sort: __call__, __and__, __or__
    '''

    def __call__(self,obj):
        '''Verify that the given object satisfies this L{TypeCheck}.

        @param obj: The object to be typechecked.
        @raise TypeError: If the object does not satisfy the type check.
        @return: None
        '''
        raise NotImplementedError("Abstract method")

    def __and__(self,other):
        '''
        Make a new composite L{TypeCheck} that expresses the logical AND of
        its components (self and other). For example, a "list of strings"
        pseudo-type could be defined as::
            instanceOf(list) & containerOf(str)

        @param other: The other L{TypeCheck} component.
        @type other: L{TypeCheck}
        @return: A L{TypeCheck} that accepts an object if and only if both
            components accept it.
        @rtype: L{TypeCheck}
        '''
        other = adapt(other, TypeCheck)
        class CompositeCheck(TypeCheck):
            def __call__(my,obj):
                self(obj); other(obj)
            def __str__(my):
                return "%s & %s" % (self, other)
        return CompositeCheck()

    def __or__(self,other):
        '''
        Make a new composite L{TypeCheck} that expresses the logical OR of its
        components (self and other). For example, a "number" pseudo-type
        can be defined as::
            instanceOf(int) | instanceOf(float) | instanceOf(complex)

        @param other: The other L{TypeCheck} component.
        @type other: L{TypeCheck}
        @return: A L{TypeCheck} that accepts an object if and only if either
            component accepts it.
        @rtype: L{TypeCheck}
        '''
        other = adapt(other, TypeCheck)
        class CompositeCheck(TypeCheck):
            def __call__(my,obj):
                try: self(obj)
                except TypeError:
                    try: other(obj)
                    except TypeError:
                        raise TypeError("%s or %s expected (%s given)" %
                                        (self, other, _typename(obj)))
            def __str__(my):
                return "%s | %s" % (self, other)
        return CompositeCheck()

    # allow 'type & typecheck' as equivalent of 'typecheck & type'
    __rand__ = __and__
    # allow 'type | typecheck' as equivalent of 'typecheck | type'
    __ror__ = __or__


class instanceOf(TypeCheck):
    '''Check for accepting a specific python type or class and its subclasses.'''

    advise(instancesProvide = [TypeCheck],
           asAdapterForTypes = [types.TypeType, types.ClassType])

    def __init__(self,typeOrClass):
        '''@param typeOrClass: A python type or class.'''
        try:
            isinstance(None,typeOrClass)
            self._type = typeOrClass
        except TypeError:
            raise TypeError("type or class expected (%s given)" %
                            _typename(typeOrClass))

    def __call__(self,obj):
        if not isinstance(obj,self._type):
            raise TypeError("%s expected (%s given)" % (self, _typename(obj)))

    def __str__(self):
        return self._type.__name__


class typeIs(instanceOf):
    '''Check for accepting a specific python type or class.

    Rarely necessary; in most cases L{instanceOf} should be used instead.
    '''

    def __call__(self,obj):
        try:
            ok = obj.__class__ is self._type
        except AttributeError:
            # 'classic' python classes don't have __class__ attribute
            # XXX: are there other things without __class__ ? i don't know
            import types
            assert type(obj) is types.ClassType, \
                  "Unexpected '__class__'-less object: %s" % obj
            ok = type(obj) is self._type
        if not ok:
            raise TypeError("%s expected (%s given)" % (self, _typename(obj)))


class containerOf(TypeCheck):
    '''Check for iterable container templates.

    The container's items have to satisfy a given L{TypeCheck} for this check
    to succeed.

    Examples:
        - containerOf(str): A container of strings.
        - containerOf(containerOf(object)): A container of containers.
        - containerOf(int, size=12): A fixed-size container of integers.
        - containerOf(float, size=lambda n: n>2 and n%2==1): A container of
          floats whose size is greater than 2 and even.
    '''

    def __init__(self, itemCheck, size=None):
        '''
        @param itemCheck: The check for the container's items.
        @type itemCheck: L{TypeCheck}, type or class.
        @param size: If not None, constrains the container's size.
        @type size: None, int (for exact size) or a predicate f(n) that
            returns True if a container of size n is valid.
        '''
        self._itemCheck = adapt(itemCheck, TypeCheck)
        self._size = size

    def __str__(self):
        return "container<%s>" % self._itemCheck

    def __call__(self,obj):
        asked_size= self._size
        if asked_size is not None:
            real_size = len(obj)
            if isinstance(asked_size,int):
                if asked_size != real_size:
                    raise TypeError("container of size %d expected "
                                    "(%s given)" % (asked_size, obj))
            elif not asked_size(real_size):
                raise TypeError("wrong container size ('%s')" % obj)
        try:
            itemCheck = self._itemCheck
            for item in obj:
                itemCheck(item)
        except TypeError:
            raise TypeError("%s expected (%s given)" % (self, obj))


def tupleOf(itemCheck, size=None):
    '''Check for tuple templates.

    @param itemCheck: The check for the tuples's items.
    @type itemCheck: L{TypeCheck}, type or class.
    @param size: If not None, constrains the tuple's size.
    @type size: None, int (for exact size) or a predicate f(n) that returns
        True if a tuple of size n is valid.
    @rtype: L{TypeCheck}
    '''
    return instanceOf(tuple) & containerOf(itemCheck,size)


def listOf(itemCheck, size=None):
    '''Check for list templates.

    @param itemCheck: The check for the list's items.
    @type itemCheck: L{TypeCheck}, type or class.
    @param size: If not None, constrains the list's size.
    @type size: None, int (for exact size) or a predicate f(n) that returns
        True if a list of size n is valid.
    @rtype: L{TypeCheck}
    '''
    return instanceOf(list) & containerOf(itemCheck,size)


def setOf(itemCheck, size=None):
    '''Check for set (sets.BaseSet) templates.

    @param itemCheck: The check for the sets's items.
    @type itemCheck: L{TypeCheck}, type or class.
    @param size: If not None, constrains the set's size.
    @type size: None, int (for exact size) or a predicate f(n) that returns
        True if a set of size n is valid.
    @rtype: L{TypeCheck}
    @require: python 2.3+
    '''
    from sets import BaseSet
    return instanceOf(BaseSet) & containerOf(itemCheck,size)


class recordOf(TypeCheck):
    '''Check for 'records', fixed size containers of 'fields' with given types.

    Examples:
        - recordOf(int,str): A record with two fields, an int and a string.
        - recordOf(float, recordOf(int,int), listOf(str)): A record of three
        fields: an int, a nested record of two integers and a list of strings.
    '''

    def __init__(self, *itemChecks):
        '''
        @param itemChecks: Each itemCheck specifies the check for the
            respective field of the record.
        @type itemChecks: Sequence of L{typechecks <TypeCheck>}, types or
            classes.
        '''
        self._itemChecks = [adapt(check,TypeCheck) for check in itemChecks]

    def __call__(self,obj):
        if len(obj) != len(self._itemChecks):
            raise TypeError("record of %d fields expected (%d given)" %
                            (len(self._itemChecks), len(obj)))
        try:
            for item,itemCheck in izip(obj, self._itemChecks):
                itemCheck(item)
        except TypeError:
            raise TypeError("%s expected (%s given)" % (self, obj))

    def __str__(self):
        return "record<%s>" % ",".join(map(str,self._itemChecks))


class mappingOf(TypeCheck):
    '''Check for mapping templates.

    Examples:
        - mappingOf(str): mapping with string keys.
        - mappingOf(value=listOf(int)): mapping with lists of integers for
          values.
        - mappingOf(tupleOf(float), setOf(int)): mapping with tuples of floats
          for keys and sets of integers for values.
    '''
    def __init__(self, key=object, value=object):
        '''
        @param key: The check for the mapping's keys.
        @param value: The check for the mapping's values.
        @type key,value: L{TypeCheck}, type or class.
        '''
        keyCheck,valueCheck = [adapt(check,TypeCheck) for check in key,value]
        typesStr = ["*","*"]
        if value is object:
            # 1. check only keys
            typesStr[0] = str(keyCheck)
            verify = containerOf(key).__call__
            self._verify = lambda mapping: verify(mapping.iterkeys())
        else:
            typesStr[1] = str(valueCheck)
            if key is object:
                # 2. check only values
                verify = containerOf(value).__call__
                self._verify = lambda mapping: verify(mapping.itervalues())
            else:
                # 3. check both keys and values
                typesStr[0] = str(keyCheck)
                def verify(obj):
                    for k,v in obj.iteritems():
                        keyCheck(k); valueCheck(v)
                self._verify = verify
        self._itemTypeStr = ",".join(typesStr)

    def __call__(self,obj):
        try: return self._verify(obj)
        except TypeError:
            raise TypeError("%s expected (%s given)" % (self, obj))

    def __str__(self):
        return "mapping<%s>" % self._itemTypeStr


def dictOf(key=object, value=object):
    '''Check for dict templates.

    @param key: The check for the mapping's keys.
    @param value: The check for the mapping's values.
    @type key,value: L{TypeCheck}, type or class.
    @rtype: L{TypeCheck}
    '''
    return instanceOf(dict) & mappingOf(key,value)


#======= Enforcing the type checks ===========================================

def typecheck(vars=None, **checkedVars):
    '''Typecheck a set of named variables.

    Example:
        >>> from typecheck import *
        >>> def f(x,y):
        ...     typecheck(x=str, y=listOf(int))
        >>> f('1',[2,3])
        >>> f(1,[2,3])
        Traceback (most recent call last):
        (...)
        TypeError: str expected (int given)
        >>> f('1',(2,3))
        Traceback (most recent call last):
        (...)
        TypeError: list expected (tuple given)
        >>> f('1',[2,'3'])
        Traceback (most recent call last):
        (...)
        TypeError: container<int> expected ([2, '3'] given)

    @param vars: Dictionary of a scope's variables, with the variables' names
        for keys and the respective variable values for values. By default, it
        is set to the locals of the caller's frame.
    @param checkedVars: A set of C{var=typecheck} keyword arguments for the
        variables to be typechecked.
    @raise TypeError: If any L{TypeCheck} fails.
    @raise ValueError: If a variable in checkedVars is not in vars.
    '''
    if vars is None:
        import sys
        vars = sys._getframe(1).f_locals
    for var,check in checkedVars.iteritems():
        try:
            value = vars[var]
        except KeyError:
            raise ValueError("Unknown variable '%s'" % var)
        else:
            adapt(check,TypeCheck)(value)

def returns(check):
    '''Typecheck the returned value from a function.

    In python 2.4+, the typical use is in function decorators:
        >>> from typecheck import *
        >>> @returns(tupleOf(int, size=3))
        ... def f(x):
        ...     y = x+x; z = x*2
        ...     return y,z,y==z
        >>> f(5)
        (10, 10, True)
        >>> f([5])
        Traceback (most recent call last):
        (...)
        TypeError: container<int> expected (([5, 5], [5, 5], True) given)

    @param check: L{TypeCheck}, type or class.
    @return: A higher-level function that accepts a function f for argument
        and returns a proxy of f that performs runtime type checking on f's
        returned value.
    '''
    if not __debug__:
        return lambda func: func
    check = adapt(check,TypeCheck)
    def closure(func):
        def typecheckedFunc(*args,**kwds):
            r = func(*args,**kwds)
            check(r)
            return r
        return typecheckedFunc
    return closure


def params(**checkedArgs):
    '''Specify the expected argument types of a function.

    In python 2.4+, the typical use is in function decorators:
        >>> from typecheck import *
        >>> @params(x=str, y=listOf(int))
        ... def f(x,y):
        ...     pass
        >>> f('1',[2,3])
        >>> f(1,[2,3])
        Traceback (most recent call last):
        (...)
        TypeError: str expected (int given)
        >>> f('1',(2,3))
        Traceback (most recent call last):
        (...)
        TypeError: list expected (tuple given)
        >>> f('1',[2,'3'])
        Traceback (most recent call last):
        (...)
        TypeError: container<int> expected ([2, '3'] given)

    @param checkedArgs: A set of C{arg=typecheck} keyword arguments for the
        parameters of the function to be typechecked.
    @return: A higher-level function that accepts a function f for argument
        and returns a proxy of f that performs runtime type checking on f's
        arguments.
    '''
    if not __debug__:
        return lambda func: func
    return lambda func: _TypeCheckedFunction(func,**checkedArgs)


#======= 'private' module definitions  =======================================

class _TypeCheckedFunction:
    '''A function proxy that performs strict runtime type checking.'''

    def __init__(self, function, **checkedArgs):
        '''
        @param function: The function to be typechecked.
        @param checkedArgs: A set of C{arg=typecheck} keyword arguments for
            the parameters of C{function} to be typechecked.
        '''
        import inspect
        self._funcspec = list(inspect.getargspec(function))
        self._function = function
        # set the defaults to empty tuple if there are no defaults
        if self._funcspec[-1] is None:
            self._funcspec[-1] = ()
        typicalArgs = list(self._funcspec[0])
        # add varargs and varkw (if present) to the typical args
        for i in 1,2:
            var = self._funcspec[i]
            if var: typicalArgs.append(var)
        # check if all the args in checkedArgs are actually function's typical
        # arguments
        for var in checkedArgs:
            if var not in typicalArgs:
                raise ValueError("Unknown typical argument '%s'" % var)
        self._checkedArgs = checkedArgs

    def __call__(self,*args,**kwds):
        '''
        Typecheck the passed arguments and then call the wrapped function,
        only if the check succeeds.
        '''
        typecheck(self._getParamsDict(*args, **kwds), **self._checkedArgs)
        return self._function(*args,**kwds)

    def _getParamsDict(self, *argvals, **kwdvals):
        '''
        Remap the passed *argvals and **kwdvals to the wrapped function's
        formal arguments.

        @return: A dict that maps each formal argument of the wrapped function
            to the respective passed value.
        '''
        args,varargs,varkw,defaults = self._funcspec
        params = dict(izip(args,argvals))
        num_args, num_argvals, num_defaults = map(len,(args,argvals,defaults))
        has_keywds = bool(kwdvals)
        for arg in args:
            if arg in kwdvals:
                if arg in params:
                    raise TypeError("%s() got multiple values for keyword "
                                    "argument '%s'" %
                                    (self._function.func_name,arg))
                else:
                    params[arg] = kwdvals.pop(arg)
        if defaults:
            for arg,val in izip(args[-num_defaults:],defaults):
                if arg not in params:
                    params[arg] = val
        for arg in args:
            if arg not in params:
                num_required = num_args - num_defaults
                raise TypeError("%s() takes at least %d %s"
                                "argument%s (%d given)" % (
                                    self._function.func_name,
                                    num_required,
                                    has_keywds and "non-keyword " or "",
                                    num_required>1 and "s" or "",
                                    num_argvals))
        if varkw:
            params[varkw] = kwdvals
        elif kwdvals:
            aKey = kwdvals.iterkeys().next()
            raise TypeError("%s() got an unexpected keyword argument '%s'"%
                            (self._function.func_name, aKey))
        if varargs:
            # if there are remaining values, set them as varargs
            if num_argvals > num_args:
                params[varargs] = argvals[-(num_argvals-num_args):]
            else:
                params[varargs] = ()
        elif num_args < num_argvals:
            raise TypeError("%s() takes %s %d argument%s (%d given)" %
                            (self._function.func_name,
                             defaults and "at most" or "exactly",
                             num_args, num_args>1 and "s" or "", num_argvals))
        return params

def _typename(obj):
    '''Return the name of the object's type.'''
    try: return obj.__class__.__name__
    except AttributeError:
        return type(obj).__name__


#=============================================================================

if __name__ == '__main__':
    # the doctests require python2.4+ to succeed
    #import doctest; doctest.testmod()
    class Class: pass
    def foo(x,y):
        pass
    foo = params(x=int, y=Class)(foo)
    foo(1, Class())

