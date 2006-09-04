#TODO: extra tests for asserting correct order

from itertools import ifilter,ifilterfalse,chain,tee
import sets

_set_types = (set,frozenset,sets.BaseSet)

__all__ = ['InsertionOrderedSet']


class InsertionOrderedSet(set):
    '''
    A set with iteration ordering defined by the the order in which elements
    were inserted into the set (insertion-order).
    '''

    __slots__ = ['_list']

    def __init__(self, iterable=()):
        self._list = []
        super(InsertionOrderedSet,self).__init__()
        self._update(iterable)

    def __iter__(self):
        return iter(self._list)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self._list)

    #--- Standard set operations ---------------------------------------------

    def __or__(self, other):
        """Return the union of two sets as a new set.

        (I.e. all elements that are in either set.)
        """
        if not isinstance(other, _set_types):
            return NotImplemented
        return self.union(other)

    def union(self, other):
        '''Return the union of two sets as a new set.

        (I.e. all elements that are in either set.)
        '''
        result = self.__class__(self)
        result._update(other)
        return result

    def __and__(self, other):
        """Return the intersection of two sets as a new set.

        (I.e. all elements that are in both sets.)
        """
        if not isinstance(other, _set_types):
            return NotImplemented
        return self.intersection(other)

    def intersection(self, other):
        '''Return the intersection of two sets as a new set.

        (I.e. all elements that are in both sets.)
        '''
        if not isinstance(other, _set_types):
            other = set(other)
        return self.__class__(ifilter(other.__contains__, self))

    def __xor__(self, other):
        """Return the symmetric difference of two sets as a new set.

        (I.e. all elements that are in exactly one of the sets.)
        """
        if not isinstance(other, _set_types):
            return NotImplemented
        return self.symmetric_difference(other)

    def symmetric_difference(self, other):
        '''Return the symmetric difference of two sets as a new set.

        (I.e. all elements that are in exactly one of the sets.)
        '''
        if not isinstance(other, _set_types):
            other = self.__class__(other)   # preserve the order in other too
        return self.__class__(chain(ifilterfalse(other.__contains__, self),
                                    ifilterfalse(self.__contains__, other)))

    def  __sub__(self, other):
        """Return the difference of two sets as a new Set.

        (I.e. all elements that are in this set and not in the other.)
        """
        if not isinstance(other, _set_types):
            return NotImplemented
        return self.difference(other)

    def difference(self, other):
        '''Return the difference of two sets as a new Set.

        (I.e. all elements that are in this set and not in the other.)
        '''
        if not isinstance(other, _set_types):
            other = set(other)
        return self.__class__(ifilterfalse(other.__contains__, self))

    #--- Mutating set operations ---------------------------------------------

    def __ior__(self, other):
        '''Update a set with the union of itself and another.'''
        self._binary_sanity_check(other)
        self.union_update(other)
        return self

    def union_update(self, other):
        '''Update a set with the union of itself and another.'''
        self._update(other)

    def __iand__(self, other):
        '''Update a set with the intersection of itself and another.'''
        self._binary_sanity_check(other)
        self.intersection_update(other)
        return self

    def intersection_update(self, other):
        '''Update a set with the intersection of itself and another.'''
        if not isinstance(other, _set_types):
            other = set(other)
        common = filter(other.__contains__, self)
        self.clear()
        self._update(common)

    def __ixor__(self, other):
        '''Update a set with the symmetric difference of itself and another.'''
        self._binary_sanity_check(other)
        self.symmetric_difference_update(other)
        return self

    def symmetric_difference_update(self, other):
        '''Update a set with the symmetric difference of itself and another.'''
        if not isinstance(other, _set_types):
            other = set(other)
        add,remove = self.add,self.remove
        for elt in other:
            (elt in self and remove or add)(elt)

    def __isub__(self, other):
        '''Remove all elements of another set from this set.'''
        self._binary_sanity_check(other)
        self.difference_update(other)
        return self

    def difference_update(self, other):
        '''Remove all elements of another set from this set.'''
        for elt in ifilter(self.__contains__, other):
            self.remove(elt)

    #--- Other mutating operations -------------------------------------------

    def add(self, element):
        '''Add an element to a set.

        This has no effect if the element is already present.
        '''
        if element not in self:
            super(InsertionOrderedSet,self).add(element)
            self._list.append(element)

    def remove(self, element):
        '''Remove an element from a set; it must be a member.

        If the element is not a member, raise a KeyError.
        '''
        super(InsertionOrderedSet,self).remove(element)
        self._list.remove(element)

    def pop(self):
        '''Remove and return an arbitrary set element.'''
        result = super(InsertionOrderedSet,self).pop()
        self._list.remove(result)
        return result

    def clear(self):
        '''Remove all elements from this set.'''
        super(InsertionOrderedSet,self).clear()
        del self._list[:]

    #--- Copying and pickling ------------------------------------------------

    def copy(self):
        '''Return a shallow copy of a set.'''
        result = super(InsertionOrderedSet,self).copy()
        result._list = list(self._list)
        return result

    __copy__ = copy # For the copy module

    def __deepcopy__(self, memo):
        '''Return a deep copy of a set; used by copy module.'''
        from copy import deepcopy
        result = self.__class__()
        memo[id(self)] = result
        for elt in self:
            result.add(deepcopy(elt, memo))
        return result

    # XXX: __builtin__.set.__getstate__ cannot be subclassed currently
    if set is sets.Set:
        def __getstate__(self):
            return super(InsertionOrderedSet,self).__getstate__(), self._list

        def __setstate__(self, state):
            sup_state, self._list = state
            super(InsertionOrderedSet,self).__setstate__(sup_state)

    #--- Assorted helpers ----------------------------------------------------

    def _update(self, iterable):
        for elt in ifilterfalse(self.__contains__, iterable):
            self.add(elt)

    def _repr(self):
        return '%s(%r)' % (self.__class__.__name__, self._list)

    def _binary_sanity_check(self, other):
        # Check that the other argument to a binary operation is also
        # a set, raising a TypeError otherwise.
        if not isinstance(other, _set_types):
            raise TypeError, 'Binary operation only permitted between sets'
