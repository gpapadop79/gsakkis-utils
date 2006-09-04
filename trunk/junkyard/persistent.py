import sys,os

_XXX_ = 1
def make_persistent(binary=False, debug=False):

    # XXX: has to be imported here instead of global scope because during
    # finalization globals are set to None
    from cPickle import dump, load

    #--- Transaction ---------------------------------------------------------

    class Transaction(object):
        #__slots__ = '_changed', '_picklename'

        def __init__(self, *args, **kwds):
            if type(self) is Transaction:
                raise TypeError('Mixin class; cannot be instantiated directly')
            self._changed = True
            self._picklename = self.getPickleFilename(*args, **kwds)

        def __setattr__(self, attr, val):
            # Subclasses must call this first
            if attr not in ('_changed', '_picklename'): #Transaction.__slots__:
                self._changed = True
            #else:
            #    parent = super(type(self),self).__setattr__
            #    print "QW", parent
            #    if parent is not Transaction:
            #        parent = object
            #    parent.__setattr__(self,attr,val)
            #    if debug: print "Changed", attr

        def commit(self):
            if self._changed or not os.path.exists(self._picklename):
                picklefile = open(self._picklename,binary and 'wb' or 'w')
                try:
                    dump(self, picklefile, binary)
                    self._changed = False
                    picklefile.close()
                    if debug: print 'Saved', self
                except:
                    self._changed = True
                    picklefile.close()
                    raise

        def rollback(self):
            if self._changed:
                if not os.path.exists(self._picklename):
                    raise Transaction.Error("Cannot rollback before commit")
                new = load(open(self._picklename))
                assert type(new) is type(self)
                if debug: print 'Loaded', new
                if hasattr(new, '__getstate__'):
                    state = new.__getstate__()
                else:
                    state = new.__dict__
                if hasattr(self, '__setstate__'):
                    self.__setstate__(state)
                else:
                    self.__dict__.update(state)
                self._changed = False

        class Error(Exception):
            pass


    #--- PersistentMeta ------------------------------------------------------

    class PersistentMeta(type):
        def __new__(meta, clsname, bases, clsdict):
            assert Transaction not in bases
            if _XXX_:
                cls = type.__new__(meta, clsname, bases, clsdict)
            else:
                cls = type.__new__(meta, clsname, (Transaction,)+bases, clsdict)
            if not hasattr(cls, 'getPickleFilename'):
                raise TypeError('getPickleFilename() undefined in %s' % cls)

            old__init__ = cls.__init__
            def __init__(self, *args, **kwds):
                Transaction.__init__(self,*args, **kwds)
                if os.path.exists(self._picklename):
                    self.rollback()
                else:
                    old__init__(self, *args, **kwds)
            if _XXX_: clsdict['__init__'] = __init__
            else: cls.__init__ = __init__

            old__setattr__ = cls.__setattr__
            def __setattr__(self, attr, val):
                Transaction.__setattr__(self,attr,val)
                old__setattr__(self,attr,val)
            if _XXX_: clsdict['__setattr__'] = __setattr__
            else: cls.__setattr__ = __setattr__

            #old__del__ = getattr(cls, '__del__', None)
            #if old__del__ is not None:
            #    def __del__(self):
            #        try: old__del__()
            #        except: pass
            #        self.commit()
            #    if _XXX_: clsdict['__del__'] = __del__
            #    else: cls.__del__ = __del__
            #else:
            #    if _XXX_: clsdict['__del__'] = Transaction.commit
            #    else: cls.__del__ = Transaction.commit

            if _XXX_:
                cls = type.__new__(meta, clsname, (cls,Transaction), clsdict)
            return cls
    return PersistentMeta



if __name__ == '__main__':


    class Test(object):

        __metaclass__ = make_persistent(debug=1)

        #__slots__ = ['id']

        def __init__(self, id):
            self.id = id
            import time; time.sleep(2)

        def getPickleFilename(self, id):
            return "%s.dat" % id


    class Foo(object):

        __slots__ = ['id']


        def __init__(self): self.id = 0

        def getPickleFilename(self, id):
            return "%s.bgw" % id


    class FooChild(Foo):

        def getPickleFilename(self, id):
            return self.__slots__, self.__dict__, self.id
            #return super(TestChild,self).getPickleFilename(id)

    t = Test(1)
    t.id += 1
    print t.id
    t.rollback();print t.id

    t.commit()
