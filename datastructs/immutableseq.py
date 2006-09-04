'''An immutable sequence type providing memory efficient slicing.'''

from copy import copy
from itertools import izip,imap,islice,chain

from common.comparable import Comparable

__author__ = "George Sakkis <gsakkis@rutgers.edu>"
__all__ = ["ImmutableSequence"]


class ImmutableSequence(object):
    '''An immutable sequence type providing memory efficient slicing.

    This class can be used as a memory efficient replacement of C{tuple} if
    a large read-only sequence needs to be sliced many times and most slices
    have length larger than 5.

    B{Caveat:} Each ImmutableSequence slice is a view of (i.e. it keeps a
    reference to) the original sequence (or a tuple copy of it, if the
    original sequence is not a tuple). This means that the original sequence
    cannot be garbage collected. For example in::
        a = ImmutableSequence(xrange(100000))
        b = a[:10]
        del a
    the memory required to store C{a} cannot be garbage collected after C{del
    a}. Hopefully such cases are rare.
    '''

    __metaclass__ = Comparable
    __slots__ = '_sequence', '_len', '_slicetuple'

    def __init__(self, iterable):
        if isinstance(iterable,ImmutableSequence):
            self._sequence = iterable._sequence
            self._len = iterable._len
            self._slicetuple = iterable._slicetuple
            return
        if not isinstance(iterable, tuple):
            iterable = tuple(iterable)
        self._sequence = iterable
        self._len = len(iterable)
        self._slicetuple = (0, self._len , 1)

    def __len__(self):
        return self._len

    def __iter__(self):
        return imap(self._sequence.__getitem__, xrange(*self._slicetuple))

    def __getitem__(self, indexOrSlice):
        size = len(self)
        if isinstance(indexOrSlice,int):
            if indexOrSlice < 0:
                indexOrSlice += size
            if 0<= indexOrSlice < size:
                start,stop,step = self._slicetuple
                return self._sequence[start + indexOrSlice*step]
            raise IndexError("%s index out of range" % _typename(self))
        # else it's a slice object
        newSequence = copy(self)
        old_start,old_stop,old_step = self._slicetuple
        start,stop,step = indexOrSlice.indices(size)
        new_start = old_start + start*old_step
        new_stop = old_start + stop*old_step
        new_step = old_step * step
        div,mod = divmod(new_stop-new_start, new_step)
        newSequence._len = max(0,div + (mod!=0))
        newSequence._slicetuple = (new_start, new_stop, new_step)
        return newSequence

    def __add__(self,other):
        if isinstance(other,ImmutableSequence):
            return ImmutableSequence(chain(self,other))
        selftype = _typename(self)
        raise TypeError('can only concatenate %s (not "%s") to '
                        '%s' % (selftype,_typename(other),selftype))

    def __mul__(self,num):
        try:
            # chain [num] iterators of self together
            return ImmutableSequence(chain(*imap(lambda n:iter(self),
                                                  xrange(num))))
        except TypeError:
            raise TypeError("can't multiply sequence to non-int")

    __rmul__ = __mul__

    def __str__(self):
        return "<%s>" % ', '.join(imap(repr,self))

    def __repr__(self):
        return "%s([%s])" % (self.__class__.__name__,
                             ', '.join(imap(repr,self)))

    def __eq__(self,other):
        if not isinstance(other,ImmutableSequence) or len(self) != len(other):
            return False
        for i,j in izip(self,other):
            if i!=j:
                return False
        return True

    def __gt__(self,other):
        if not isinstance(other,ImmutableSequence):
            raise TypeError("Cannot compare ImmutableSequence to %s" %
                            _typename(other))
        diff = len(self) - len(other)
        if diff>0: return True
        if diff<0: return False
        for i,j in izip(self,other):
            if i>j:
                return True
        return False


def _typename(obj):
    try: return obj.__class__.__name__
    except AttributeError:
        return type(obj).__name__
