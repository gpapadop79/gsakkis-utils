#from memento import MementoMetaclass

class TypeChecker(object):
    '''Abstract base class for runtime type checking.
    
    The exact definition of a "type" is left for the extending subclasses.
    Thus a "type" can be more general that a python type; for example 
    types like "strings of length 5", "lists of integers",
    "dictionaries with string keys and tuples of float as values", etc.
    can be defined. Then at runtime any object can be verified against
    such types.
    '''
    
    # TypeChecker instances are cached
    #__metaclass__ = MementoMetaclass
    
    def verify(*objectCheckerPairs):
        '''Verify that a number of objects satisfy the respective TypeCheckers.
            
        @param objectCheckerPairs: A sequence of (object,typeOrChecker) pairs
            where typeOrChecker can be either a python type or a TypeChecker
            instance. In the first case, the object passes the test
            iff isinstance(object,typeOrChecker) is True. For instance:
                TypeChecker.verify((age, int), (emails,ListOf(Email)))
            
        @return: True
        @raise TypeError: If any object does not satisfy its respective
            typeOrChecker
        '''
        make = TypeChecker._make
        try:
            for obj,typeOrChecker in objectCheckerPairs:
                checker = make(typeOrChecker)
                checker._verify(obj)
        except TypeError:
            raise TypeError, "%s: Expected '%s'" % (obj,checker._typeStr())
        return True
    verify = staticmethod(verify)
    
    def _typeStr(self):
        '''Return a human readable description of the type accepted by this checker.
        
           Abstract method.
        '''
        raise NotImplementedError("Abstract method")
    
    def _verify(self,obj):
        '''Verify that the given object satisfies this TypeChecker.
            
           Abstract method. It should raise a TypeError if the object
           does not satisfy the type checker; otherwise it should return
           normally (the return value is ignored).
        '''
        raise NotImplementedError("Abstract method")
    
    def __and__(self,other):
        '''Return a TypeChecker instance that verifies an object if and
           only if both arguments (TypeChecker instances) verify the object.
           
           Example: the "type" "list of strings" can be defined as:
                InstanceOf(list) & ContainerOf(str)
        '''
        class CompositeChecker(TypeChecker):
            def _verify(my,obj):
                self._verify(obj)
                other._verify(obj)
            def _typeStr(my):
                return "%s & %s" % (self._typeStr(), other._typeStr())
        return CompositeChecker()
                
    def __or__(self,other):
        '''Return a TypeChecker instance that verifies an object if either
           of the arguments (TypeChecker instances) verify the object.
           
           Examples: InstanceOf(int) | InstanceOf(float)
        '''
        class CompositeChecker(TypeChecker):
            def _verify(my,obj):
                try: self._verify(obj)
                except TypeError: other._verify(obj)
            def _typeStr(my):
                return "%s | %s" % (self._typeStr(), other._typeStr())
        return CompositeChecker()
    
    def _make(typeOrChecker):
        '''Factory method to return a TypeChecker instance.
        
           typeOrChecker -- Either a TypeChecker instance or a type instance
            If it's a TypeChecker, it is returned immediately.
            If it's a type, an InstanceOf(type) TypeChecker instance is returned.
        '''
        if isinstance(typeOrChecker, TypeChecker):
            return typeOrChecker
        return InstanceOf(typeOrChecker)
    _make = staticmethod(_make)
    
    
from inspect import isclass
class InstanceOf(TypeChecker):
    '''A simple TypeChecker wrapper for python types and classes.
    
       An object satisfies it if isinstance(object,type) yields True.
    '''
    def __init__(self,aType):
        if not isclass(aType):
            raise TypeError("%s expects a type argument (%s given)" % (
                             self.__init__,type(aType).__name__))
        self._type = aType
    def _typeStr(self):
        return self._type.__name__
    def _verify(self,obj):
        if not isinstance(obj,self._type):
            raise TypeError()


class ContainerOf(TypeChecker):
    '''A TypeChecker that accepts containers (or more generally iterators)
       whose elements satisfy one (or more) given types or TypeChecker(s). 
    
       Examples:
         ContainerOf(str) : container of (any number of) strings
         ContainerOf(int,str): container of two elements, an int and a string
         ContainerOf(str, ContainerOf(object), float) : container of 3 elements:
            the first must be a string, the second a generic container
            and the third a float.
    '''
    
    def __init__(self, itemType, *restItemTypes):
        '''ContainerOf constructor.
        
            itemType  -- A python type,class or TypeChecker
            restItemTypes -- Optional other types,classes and TypeCheckers.
              - if no restTypes is given, this TypeChecker accepts any
              container whose elements are verified by itemType;
              - otherwise, this TypeChecker accepts only containers of
              size len(restTypes)+1, whose i-th element is accepted by
              the i-th type or the list [itemType]+restTypes.
        '''                    
        if not restItemTypes:
            itemChecker = TypeChecker._make(itemType)
            self._itemTypeStr = itemChecker._typeStr()
            def verify(obj):
                for item in obj:
                    itemChecker._verify(item)
        else:
            itemTypes = (itemType,) + restItemTypes
            itemCheckers = tuple([TypeChecker._make(aType) for aType in itemTypes])
            self._itemTypeStr = ",".join([aChecker._typeStr() for aChecker in itemCheckers])
            def verify(obj):
                # make sure that obj and itemCheckers have the same number of elements
                iterCheckers = iter(itemCheckers)
                for item in obj:
                    try: iterCheckers.next()._verify(item)
                    except StopIteration: raise TypeError()
                try: iterCheckers.next()
                except StopIteration: pass
                else: raise TypeError()
        self._verify = verify
    
    def _typeStr(self):
        return "container<%s>" % self._itemTypeStr
    
class TypedContainerOf(TypeChecker):
    '''A TypeChecker for containers of a given type.'''
    def __new__(cls, containerType, itemType, *restItemTypes):
        containerChecker = InstanceOf(containerType)
        itemChecker = ContainerOf(itemType, *restItemTypes)
        self = containerChecker & itemChecker
        self._itemTypeStr = itemChecker._itemTypeStr
        typeStr = "%s<%s>" % (containerChecker._typeStr(),
                              self._itemTypeStr)
        self._typeStr = lambda : typeStr
        return self

class TupleOf(TypedContainerOf):
    '''A TypeChecker for tuples whose elements satisfy a given TypeChecker.'''
    def __new__(cls,itemType,*restItemTypes):
        return TypedContainerOf.__new__(cls,tuple,itemType,*restItemTypes)

class ListOf(TypeChecker):
    '''A TypeChecker for lists whose elements satisfy a given TypeChecker.'''
    def __new__(cls,itemType,*restItemTypes):
        return TypedContainerOf.__new__(cls,list,itemType,*restItemTypes)

class SetOf(TypedContainerOf):
    '''A TypeChecker for sets whose elements satisfy a given TypeChecker.'''
    def __new__(cls,itemType):
        from sets import Set
        return TypedContainerOf.__new__(cls,Set,itemType)


class MappingOf(TypeChecker):
    '''A TypeChecker for mappings of a given key and/or value type
      (or TypeChecker).
      
      Examples:
        MappingOf(str) : mapping with string keys
        MappingOf(valueType=ListOf(int)) : mapping with values lists of integers.
        MappingOf(TupleOf(float), SetOf(int)) : mapping with keys tuples of floats
            and values sets of integers.
    '''
    def __init__(self, keyType=object, valueType=object):
        keyChecker = TypeChecker._make(keyType)
        valueChecker = TypeChecker._make(valueType)
        typesStr = ["*","*"]
        # 1. if have to check both keys and values
        if keyType is not object and valueType is not object:
            typesStr = [checker._typeStr() for checker in keyChecker,valueChecker]
            # make a custom TypeChecker that verifies keys and values in
            # one pass
            def verify(obj):
                for key,value in obj.iteritems():
                    keyChecker._verify(key)
                    valueChecker._verify(value)
            self._verify = verify            
        # 2. else if have to check only keys
        elif keyType is not object:
            # make a custom ContainerOf TypeChecker that verifies keys
            typesStr[0] = keyChecker._typeStr()
            keyVerify = ContainerOf(keyType)._verify
            self._verify = lambda obj: keyVerify(obj.iterkeys())
        # 3. else if have to check only values
        elif valueType is not object:
            # make a custom ContainerOf TypeChecker that verifies values
            typesStr[1] = valueChecker._typeStr()
            valueVerify = ContainerOf(valueType)._verify
            self._verify = lambda obj: valueVerify(obj.itervalues())
        # 4. else don't have to check anything; not very useful
        else:
            raise ValueError("No keyType or valueType given")
        self._itemTypeStr = "%s,%s" % (typesStr[0],typesStr[1])
    
    def _typeStr(self):
        return "mapping<%s>" % self._itemTypeStr


class DictOf(TypeChecker):
    def __new__(cls, keyType=object, valueType=object):
        mapChecker = MappingOf(keyType,valueType)
        self = InstanceOf(dict) & mapChecker 
        self._itemTypeStr = mapChecker._itemTypeStr
        self._typeStr = lambda: "dict<%s>" % self._itemTypeStr
        return self


if __name__ == '__main__':
    class Child(object):
        def __init__(self,name=None): self.name = name
    class Phone(object):
        def __init__(self,num=None): self.num = num
        
    def foo(name,age,children,phonebook):
        assert TypeChecker.verify(
            (age,       int),
            (name,      TupleOf(str,str)),
            (children,  ListOf(Child)),
            (phonebook, MappingOf(str, ContainerOf(Phone)))
            )
    
    foo(name = ("Paul","Smith"),
      age = 23,
      children = [Child(),Child()],
      phonebook = {
        "Mike": (Phone(),Phone()),
        "office": [Phone()]
      })
    
