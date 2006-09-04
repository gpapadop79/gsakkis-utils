import inspect

def Namespace(prevVersion=None):
    '''Namespace metaclass factory.

    Called without an argument (the default), it returns a metaclass that
    builds a "namespace". A namespace is defined as a class whose enclosed
    classes are aware of it through the class variable '__namespace__'. Thus
    nestedclass.__namespace__ is the same as method.im_class. For example::
        >>> class Foo:
        ...     __metaclass__ = Namespace()
        ...     class Bar: pass
        >>> Foo.Bar.__namespace__
        <class '__main__.Foo'>

    The optional argument, if given, should be an existing namespace (i.e.
    a class with Namespace for metaclass). In this case, the returned metaclass
    mirrors the nested class hierarchy of the original namespace to the new
    namespace, overriding the redefined nested classes along the way.
    For example:
        >>> class MedievalAge(object):
        ...     __metaclass__ = Namespace()
        ...     class GameUnit(object):
        ...         def move(self): return "MedievalAge.GameUnit.move()"
        ...     class CombatUnit(GameUnit):
        ...         def fight(self): return "MedievalAge.CombatUnit.fight()"
        ...     class RangedUnit(CombatUnit):
        ...         def aim(self): return "MedievalAge.RangedUnit.aim()"
        >>>
        >>> class ColonialAge(object):
        ...     __metaclass__ = Namespace(MedievalAge)
        ...     class CombatUnit:
        ...         def fight(self): return "ColonialAge.CombatUnit.fight()"
        >>> print ColonialAge().GameUnit().move()
        MedievalAge.GameUnit.move()
        >>> print ColonialAge().CombatUnit().move()
        MedievalAge.GameUnit.move()
        >>> print ColonialAge().RangedUnit().move()
        MedievalAge.GameUnit.move()
        >>> print ColonialAge().CombatUnit().fight()
        ColonialAge.CombatUnit.fight()
        >>> print ColonialAge().RangedUnit().fight()
        ColonialAge.CombatUnit.fight()
        >>> print ColonialAge().RangedUnit().aim()
        MedievalAge.RangedUnit.aim()

    @param prevVersion: An existing 'namespace'
    @type prevVersion: Class
    @rtype: Metaclass
    '''
    if prevVersion is None:
        return _Namespace
    # make sure that prevVersion is actually made from _Namespace
    if not issubclass(type(prevVersion), _Namespace):
        raise TypeError("%s must have %s for __metaclass__" % (
            prevVersion, _Namespace))
    class NewNamespace(_Namespace):
        def __new__(meta, clsname, bases, clsdict):
            def buildNewInner(oldInner, cache):
                innerName = oldInner.__name__
                newInner = cache.get(innerName)
                if newInner is None:
                    # recursively build the new inner classes for all the
                    # bases of oldInner that are in defined in prevVersion
                    newInnerBases = [
                        buildNewInner(base,cache) for base in oldInner.__bases__
                        if getattr(base,'__namespace__',None) is prevVersion]
                    # include oldInner as base too
                    newInnerBases.append(oldInner)
                    try: # check if it has been redefined in this version
                        newInner = clsdict[innerName]
                        # if so, add any bases it may have
                        newInnerBases.extend(newInner.__bases__)
                        # type() needs a real dict, not dictproxy..
                        newDict = dict(newInner.__dict__)
                    except KeyError:
                        # it has not been redefined; set just the __module__
                        newDict = {'__module__' : clsdict['__module__']}
                    # create the inner class in the new version and cache it
                    newInner = cache[innerName] = type(innerName,
                                                       tuple(newInnerBases),
                                                       newDict)
                return newInner
            # collect all the inner classes of the previous version
            cache = {}
            for _,oldInner in inspect.getmembers(prevVersion):
                if hasattr(oldInner, '__namespace__'):
                    buildNewInner(oldInner,cache)
            # update the __dict__ of the new version with the new inner classes
            clsdict.update(cache)
            return type.__new__(meta, clsname, bases, clsdict)
    return NewNamespace


class _Namespace(type):
    def __init__(cls, name, bases, clsdict):
        for inner in [v for k,v in clsdict.iteritems()
                      # do not include the __metaclass__ itself !
                      if inspect.isclass(v) and k != '__metaclass__']:
            # prevent manual tweaking with __namespace__
            assert '__namespace__' not in clsdict
            inner.__namespace__ = cls
        return type.__init__(cls, name, bases, clsdict)


if __name__ == '__main__':
    import doctest; doctest.testmod()
