import os
import cPickle as pickle

__all__ = ['autopickle']


def autopickle(arg):
    '''If arg is True or False, return a decorator with binmode=arg; otherwise
    decorate the arg (should be a callable). For example:

    @autopickle
    def foo(): pass

    @autopickle(True)
    def bar(): pass
    '''
    if arg == bool(arg):
        return lambda __init__: _autopickle(__init__, arg)
    else:
        return _autopickle(arg)


def _autopickle(__init__, binmode=False):
    '''Decorator for instantiating pickled instances transparently.

    The class of the instance whose __init__ is called has to have a method
    C{getPickleFilename(*args, **kwds)} that takes the same arguments as
    __init__ and returns either::
        - a file path. In this case the decorated __init__ checks if the file
            exists and if so it tries to unpickle it; otherwise it calls the
            original __init__ and pickles the instance to the given file path.
        - or None. In this case, the original __init__ is called and no
            pickling/unpicking takes place.
    '''
    def new__init__(self, *args, **kwds):
        picklename = self.getPickleFilename(*args, **kwds)
        if picklename is None or not os.path.exists(picklename):
            __init__(self, *args, **kwds)
            if picklename is not None:
                picklefile = open(picklename, binmode and 'wb' or 'w')
                try: pickle.dump(self, picklefile, binmode)
                finally: picklefile.close()
        else:
            newSelf = pickle.load(open(picklename))
            assert type(newSelf) is type(self)
            # copy newSelf to self
            if hasattr(newSelf, '__getstate__'):
                state = newSelf.__getstate__()
            else:
                state = newSelf.__dict__
            if hasattr(self, '__setstate__'):
                self.__setstate__(state)
            else:
                self.__dict__.update(state)
    return new__init__


if __name__ == '__main__':

    class Foo(object):
        @autopickle
        def __init__(self, id):
            import time; time.sleep(2)
            self.id = id
        def getPickleFilename(self, id):
            return "%s.dat" % id

    print Foo(1)
