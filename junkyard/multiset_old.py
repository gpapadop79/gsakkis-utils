from sets import Set, ImmutableSet
from itertools import chain,imap,ifilter

__author__ = "George Sakkis <gsakkis@rutgers.edu>"
__all__ = ["MultiSet"]


class MultiSet(Set):
    __slots__ = []
    
    def __init__(self,iterable=None):
        """Construct a multiset from an optional iterable."""
        Set.__init__(self,iterable)

    # Standard protocols: __len__, __repr__, __str__, __iter__

    def __len__(self):
        """Return the number of elements of a set."""
        return len(self._data) + sum(imap(len,self._data.itervalues()))

    def __repr__(self):
        """Return string representation of a set.

        This looks like 'Set([<list of elements>])'.
        """
        elements = self._data.keys() + sum(self._data.values(), [])
        return '%s(%r)' % (self.__class__.__name__, elements)

    __str__ = __repr__

    def __iter__(self):
        """Return an iterator over the elements or a set.

        This is the keys iterator for the underlying dict.
        """
        return chain(self._data.iterkeys(),
                     *imap(iter,self._data.itervalues()))

    def __copy__(self):
        """Return a shallow copy of a set."""
        raise NotImplementedError
        #result = self.__class__()
        #result._data.update(self._data)
        #return result

    def __deepcopy__(self, memo):
        """Return a deep copy of a set; used by copy module."""
        # This pre-creates the result and inserts it in the memo
        # early, in case the deep copy recurses into another reference
        # to this same set.  A set can't be an element of itself, but
        # it can certainly contain an object that has a reference to
        # itself.
        raise NotImplementedError
        #from copy import deepcopy
        #result = self.__class__()
        #memo[id(self)] = result
        #data = result._data
        #value = True
        #for elt in self:
        #    data[deepcopy(elt, memo)] = value
        #return result

    def intersection(self, other):
        """Return the intersection of two sets as a new set.
        
        (I.e. all elements that are in both sets.)
        """
        raise NotImplementedError
        #if not isinstance(other, BaseSet):
        #    other = Set(other)
        #if len(self) <= len(other):
        #    little, big = self, other
        #else:
        #    little, big = other, self
        #common = ifilter(big._data.has_key, little)
        #return self.__class__(common)
        
    def symmetric_difference(self, other):
        """Return the symmetric difference of two sets as a new set.
        
        (I.e. all elements that are in exactly one of the sets.)
        """
        raise NotImplementedError
        #result = self.__class__()
        #data = result._data
        #value = True
        #selfdata = self._data
        #try:
        #    otherdata = other._data
        #except AttributeError:
        #    otherdata = Set(other)._data
        #for elt in ifilterfalse(otherdata.has_key, selfdata):
        #    data[elt] = value
        #for elt in ifilterfalse(selfdata.has_key, otherdata):
        #    data[elt] = value
        #return result

    def difference(self, other):
        """Return the difference of two sets as a new Set.

        (I.e. all elements that are in this set and not in the other.)
        """
        raise NotImplementedError
        #result = self.__class__()
        #data = result._data
        #try:
        #    otherdata = other._data
        #except AttributeError:
        #    otherdata = Set(other)._data
        #value = True
        #for elt in ifilterfalse(otherdata.has_key, self):
        #    data[elt] = value
        #return result

    # Subset and superset test

    def issubset(self, other):
        raise NotImplementedError
        #"""Report whether another set contains this set."""
        #self._binary_sanity_check(other)
        #if len(self) > len(other):  # Fast check for obvious cases
        #    return False
        #for elt in ifilterfalse(other._data.has_key, self):
        #    return False
        #return True

    def issuperset(self, other):
        raise NotImplementedError
        #"""Report whether this set contains another set."""
        #self._binary_sanity_check(other)
        #if len(self) < len(other):  # Fast check for obvious cases
        #    return False
        #for elt in ifilterfalse(self._data.has_key, other):
        #    return False
        #return True

    # In-place union, intersection, differences.
    # Subtle:  The xyz_update() functions deliberately return None,
    # as do all mutating operations on built-in container types.
    # The __xyz__ spellings have to return self, though.

    def __ior__(self, other):
        """Update a set with the union of itself and another."""
        self._binary_sanity_check(other)
        self._update(other)
        return self

    def __iand__(self, other):
        raise NotImplementedError        
        #"""Update a set with the intersection of itself and another."""
        #self._binary_sanity_check(other)
        #self._data = (self & other)._data
        #return self

    def symmetric_difference_update(self, other):
        """Update a set with the symmetric difference of itself and another."""
        raise NotImplementedError        
        #data = self._data
        #value = True
        #if not isinstance(other, BaseSet):
        #    other = Set(other)
        #for elt in other:
        #    if elt in data:
        #        del data[elt]
        #    else:
        #        data[elt] = value

    def difference_update(self, other):
        """Remove all elements of another set from this set."""
        raise NotImplementedError        
        #data = self._data
        #if not isinstance(other, BaseSet):
        #    other = Set(other)
        #for elt in ifilter(data.has_key, other):
        #    del data[elt]

    # Single-element mutations: add, remove, discard

    def add(self, element):
        """Add an element to a set.

        This has no effect if the element is already present.
        """
        try:
            self._add(element)
        except TypeError:
            transform = getattr(element, "__as_immutable__", None)
            if transform is None:
                raise # re-raise the TypeError exception we caught
            self._add(transform())

    def remove(self, element):
        """Remove an element from a set; it must be a member.
        
        If the element is not a member, raise a KeyError.
        """
        try:
            self._remove(element)
        except TypeError:
            transform = getattr(element, "__as_temporarily_immutable__", None)
            if transform is None:
                raise # re-raise the TypeError exception we caught
            self._remove(transform())

    def pop(self):
        """Remove and return an arbitrary set element."""
        e,lst = self._data.popitem()
        if lst:            
            self._data[e] = lst
            return lst.pop()
        else:
            return e

    # Assorted helpers
    
    def _add(self,element):
        lst = self._data.get(element, None)
        if lst is None:
            self._data[element] = []
        else:
            lst.append(element)

    def _remove(self,element):
        lst = self._data[element]
        if lst:
            lst.pop()
        else:
            del self._data[element]

    def _update(self, iterable):
        # The main loop for update() and the subclass __init__() methods.
        data = self._data
        # Use the fast update() method when a dictionary is available.
        if isinstance(iterable, MultiSet):
            for element,lst in iterable._data.iteritems():
                self_lst = data.get(element)
                if self_lst:
                    self_lst += lst
                else:
                    data[element] = lst
            return
        # general update
        for element in iterable:
            self.add(element)

    def __as_immutable__(self):
        # Return a copy of self as an immutable set
        return ImmutableSet(self)

    def __as_temporarily_immutable__(self):
        # Return self wrapped in a temporarily immutable set
        return _TemporarilyImmutableSet(self)
