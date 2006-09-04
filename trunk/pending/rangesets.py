'''Module for continuous ranges and sets of ranges.

A L{Range} represents a continuous, bounded or unbounded, interval. A
L{RangeSet} is a set of zero or more disjoint Ranges. Ranges and RangeSets are
created either directly, or, more often, by one of the handy factory methods.

Ranges support L{membership <Range.__contains__>}, L{overlap <Range.overlaps>}
and L{adjacency <Range.adjacentTo>} queries. A bounded Range whose bounds can
be subtracted has a L{length <Range.__len__>} equal to the difference of its
bounds.

RangeSets can be combined through L{union <RangeSet.__or__>}, L{intersection
<RangeSet.__and__>}, L{difference <RangeSet.__sub__>}, L{symmetric difference
<RangeSet.__xor__>} and L{complement <RangeSet.__invert__>}. RangeSets also
support L{membership <RangeSet.__contains__>} and L{overlap <RangeSet.overlaps>}
queries. Finally, a RangeSet can L{iterate <RangeSet.__iter__>} over its
disjoint Ranges.

Ranges can include any comparable objects, not just numbers. Here's an example
of using strings:

#>>> officeHours = RangeSet.closed('08:00', '17:00')
#>>> myLunch = RangeSet.closed('11:30', '12:30')
#
#>>> myHours = RangeSet.closed('08:30', '19:30') - myLunch
#>>> myHours in officeHours
#False
#>>> '12:00' in myHours
#False
#>>> '15:30' in myHours
#True
#>>> inOffice = officeHours & myHours
#>>> print inOffice
#RangeSet(['08:30','11:30'), ('12:30','17:00'])
#>>> overtime = myHours - officeHours
#>>> print overtime
#RangeSet(('17:00', '19:30'])
'''

#todo:
#   - move doctest -> unittest, more tests
#   - optimization
# ? refactoring: Range fields -> tuples
# ? immutable Range and/or RangeSet  (__hash__)
# ? mutable Range and/or RangeSet (add,remove,discard,clear,pop,copy)

import copy
from common.comparable import Comparable

__all__ = ['Range', 'RangeSet']


#======= Range ===============================================================

class Range(object):
    '''A Range represents a continuous interval of values.

    A Range is specified by a lower bound, an upper bound, and flags
    determining whether the bound is included in the Range or not. Ranges are
    usually constructed by a factory method.

    @group Subset, superset and equality predicates: issubset, __le__, __lt__,
        issuperset, __ge__, __gt__, __eq__, __ne__
    @group Other predicates: __nonzero__, isSingleton, __contains__, overlaps,
        adjacentTo
    @group Factories: open, closed, openClosed, closedOpen, lessThan,
        greaterThan, singleton, empty, full
    '''

    # generates automatically the missing comparison methods given the defined
    # ones
    __metaclass__ = Comparable

    __slots__ = 'min', 'max', 'minClosed', 'maxClosed'

    def __init__(self, min, max, closed_low, closed_up):
        '''Create a new Range.

        By default a Range is open. More general, a Range can be:
            - an empty set: C{Range(5, 5, False, False)}
            - a singleton: C{Range(82, 82, True, True)}
            - an open bounded interval: C{Range(25, 28, False, False)}
            - a closed interval: C{Range(29, 216, True, True)}
            - a half-open interval:
                - open-closed: C{Range(25, 28, False, True)}
                - closed-open: C{Range(25, 28, True, False)}
            - a half-bounded interval:
                - (24, +oo): C{Range(24, None, False, False)}
                - [24, +oo): C{Range(24, None, True, False)}
                - (-oo, 62): C{Range(None, 62, False, False)}
                - (-oo, 62]: C{Range(None, 62, False, True)}
            - the unbounded interval: C{Range(None, None, False, False)}
        It is typically easier to create a Range using one of the class method
        factories.

        @param min: The lower bound of the Range, or None for unbouded.
        @param max: The upper bound of the Range, or None for unbouded.
        @param closed_low: True if the lower bound is included in the Range.
        @param closed_up: True if the upper bound is included in the Range.
        @raise ValueError: If an infinite boundary is included.
        '''
        if min is not None and max is not None and min > max:
            raise ValueError('min cannot be greater than max')
        if min is None:
            min = _Smallest
            if closed_low:
                raise ValueError('%s cannot be included in a Range' % min)
        if max is None:
            max = _Largest
            if closed_up:
                raise ValueError('%s cannot be included in a Range' % max)
        self.min = min
        self.max = max
        self.minClosed = closed_low
        self.maxClosed = closed_up

    def __len__(self):
        '''Return the length of this Range, defined as the difference of the
        upper minus the lower bound.

        @raise ArithmeticError: If the Range is unbounded.
        @raise TypeError: If the bounds cannot be subtracted.
        '''
        if self.min is _Smallest or self.max is _Largest:
            raise ArithmeticError('len() of unbounded range')
        return self.max - self.min

    def __repr__(self):
        '''Return a string representation of this Range.'''
        if self:
            if self.isSingleton():
                return '{%s}' % self.min
            else:
                return '%s%s,%s%s' % (self.minClosed and '[' or '(',
                                      self.min, self.max,
                                      self.maxClosed and ']' or ')')
        else: # empty set
            return '{-}'

    __str__ = __repr__

    #-------- Subset, superset and equality predicates -----------------------

    def issubset(self, other):
        '''Check if this Range is a subset of another Range, RangeSet or
        iterable.

        >>> all    = Range.full()
        >>> lt     = Range.lessThan(10)
        >>> some   = Range.closed(10,20)
        >>> single = Range.singleton(10)
        >>> ge     = Range.greaterThan(10, or_equal=True)
        >>> some.issubset(all)
        True
        >>> all.issubset(lt)
        False
        >>> some.issubset(lt)
        False
        >>> single.issubset(ge)
        True
        >>> some.issubset((4,2,6))
        False
        >>> some.issubset([11,13,15])
        False

        @type other: L{Range} or any iterable.
        '''
        if isinstance(other, Range):
            # a.issubset(b) <==> b.issuperset(a); just swap self,other from
            # self.issuperset
            return (
                (other.min < self.min
                 or (other.min == self.min
                     and (other.minClosed or other.minClosed == self.minClosed)))
                and
                (other.max > self.max
                 or (other.max == self.max
                     and (other.maxClosed or other.maxClosed == self.maxClosed))))
        elif isinstance(other, RangeSet):
            return other.issuperset(self)
        else:
            other = iter(other) # raise Exception if not iterable
            if self.isSingleton():
                return self.min in other
            return False

    __le__ = issubset

    def issuperset(self, other):
        '''Check if this Range is a superset of another Range, RangeSet or
        iterable.

        >>> all    = Range.full()
        >>> lt     = Range.lessThan(10)
        >>> some   = Range.closed(10,20)
        >>> single = Range.singleton(10)
        >>> ge     = Range.greaterThan(10, or_equal=True)
        >>> some.issuperset(all)
        False
        >>> all.issuperset(lt)
        True
        >>> some.issuperset(lt)
        False
        >>> ge.issuperset(single)
        True
        >>> some.issuperset((4,2,6))
        False
        >>> some.issuperset([11,13,15])
        True

        @type other: L{Range} or any iterable.
        '''
        if isinstance(other, Range):
            return (
                (# check if we start before the other
                 self.min < other.min
                 # or at the same point with the other (provided we're not
                 # open while other is closed)
                 or (self.min == other.min
                     and (self.minClosed or self.minClosed == other.minClosed)))
                and
                (# check if we end after the other
                 self.max > other.max
                 # or at the same point with the other (provided we're not
                 # open while other is closed)
                 or (self.max == other.max
                     and (self.maxClosed or self.maxClosed == other.maxClosed))))
        elif isinstance(other,RangeSet):
            return other.issuperset(self)
        for elem in other:
            if elem not in self: return False
        return True

    __ge__ = issuperset

    def __eq__(self, other):
        '''Check if this Range is equal to another.

        >>> Range.open(1,2) == Range.closedOpen(1,2)
        False
        >>> Range.openClosed(1,2) == Range.closed(1,2)
        False
        >>> Range.open(1,1) == Range.open(3,3)  # both empty sets
        True
        '''
        non_empty = bool(self)
        if non_empty:
            return (self.min == other.min
                    and self.max == other.max
                    and self.minClosed == other.minClosed
                    and self.maxClosed == other.maxClosed)
        else: # True if both are empty
            return not bool(other)

    #-------- Other predicates -----------------------------------------------

    def isSingleton(self):
        '''Check if this Range is a singleton.'''
        return self.min == self.max and self.minClosed and self.maxClosed

    def __contains__(self, obj):
        '''Check if C{obj} is contained in this Range.

        >>> all    = Range.full()
        >>> lt     = Range.lessThan(10)
        >>> le     = Range.lessThan(10, or_equal=True)
        >>> some   = Range.closed(10,20)
        >>> single = Range.singleton(10)
        >>> ge     = Range.greaterThan(10, or_equal=True)
        >>> gt     = Range.greaterThan(10)
        >>> 10 in all
        True
        >>> 10 in lt
        False
        >>> 10 in le
        True
        >>> 10 in some
        True
        >>> 10 in single
        True
        >>> 10 in ge
        True
        >>> 10 in gt
        False
        '''
        return (
            # check if we start before obj
            (self.min < obj or (self.min == obj and self.minClosed))
            and
            # check if we end after obj
            (self.max > obj or (self.max == obj and self.maxClosed)))

    def __nonzero__(self):
        '''Check if this Range is non-empty.

        >>> bool(Range.empty())
        False
        >>> bool(Range.closedOpen(12,12))
        False
        >>> bool(Range.singleton(12))
        True
        '''
        return self.min != self.max or (self.maxClosed and self.minClosed)

    def overlaps(self, other):
        '''Check if this Range overlaps with another Range, RangeSet or
        iterable.

        >>> r1  = Range.lessThan(-100)
        >>> r2  = Range.lessThan(-100, or_equal=True)
        >>> r3  = Range.lessThan(100)
        >>> r4  = Range.lessThan(100, or_equal=True)
        >>> r5  = Range.full()
        >>> r6  = Range.open(-100,100)
        >>> r7  = Range.openClosed(-100,100)
        >>> r8  = Range.greaterThan(-100)
        >>> r9  = Range.singleton(-100)
        >>> r10 = Range.closedOpen(-100,100)
        >>> r11 = Range.closed(-100,100)
        >>> r12 = Range.greaterThan(-100, or_equal=True)
        >>> r13 = Range.greaterThan(100)
        >>> r14 = Range.singleton(100)
        >>> r15 = Range.greaterThan(100, or_equal=True)
        >>> r8.overlaps(r9)
        False
        >>> r12.overlaps(r6)
        True
        >>> r7.overlaps(r8)
        True
        >>> r8.overlaps(r4)
        True
        >>> r14.overlaps(r11)
        True
        >>> r10.overlaps(r13)
        False
        >>> r5.overlaps(r1)
        True
        >>> r5.overlaps(r2)
        True
        >>> r15.overlaps(r6)
        False
        >>> r3.overlaps(r1)
        True
        '''
        if isinstance(other,Range):
            return (
                # normal case: the lower bound of self must be less than the
                # upper bound of other, and vice versa
                self.min < other.max and self.max > other.min
                # special cases: one lower bound is equal to the other upper
                # bound overlap iff both are closed
                or
                self.min == other.max and self.minClosed and other.maxClosed
                or
                self.max == other.min and self.maxClosed and other.minClosed)
        elif isinstance(other,RangeSet):
            return other.overlaps(self)
        else:
            for i in other:
                if i in self: return True
            return False

    def adjacentTo(self, other, allow_overlap=False):
        '''Check if this Range is adjacent to the other.

        Two Ranges are adjacent they don't overlap and their union is a single
        Range. If allow_overlap is True, the two Ranges are also considered
        adjacent if they have a single point in common. For example, (3,4] and
        [4,oo) would be adjacent for allow_overlap=True despite their overlap
        at 4.

        >>> r1  = Range.lessThan(-100)
        >>> r2  = Range.lessThan(-100, or_equal=True)
        >>> r3  = Range.lessThan(100)
        >>> r4  = Range.lessThan(100, or_equal=True)
        >>> r5  = Range.full()
        >>> r6  = Range.open(-100,100)
        >>> r7  = Range.openClosed(-100,100)
        >>> r8  = Range.greaterThan(-100)
        >>> r9  = Range.singleton(-100)
        >>> r10 = Range.closedOpen(-100,100)
        >>> r11 = Range.closed(-100,100)
        >>> r12 = Range.greaterThan(-100, or_equal=True)
        >>> r13 = Range.greaterThan(100)
        >>> r14 = Range.singleton(100)
        >>> r15 = Range.greaterThan(100, or_equal=True)
        >>> r1.adjacentTo(r6)
        False
        >>> r6.adjacentTo(r11)
        False
        >>> r7.adjacentTo(r9)
        True
        >>> r3.adjacentTo(r10)
        False
        >>> r5.adjacentTo(r14)
        False
        >>> r6.adjacentTo(r15)
        True
        >>> r1.adjacentTo(r8)
        False
        >>> r12.adjacentTo(r14)
        False
        >>> r6.adjacentTo(r13)
        False
        >>> r2.adjacentTo(r15)
        False
        >>> r1.adjacentTo(r4)
        False
        '''
        if self.max == other.min:
            if allow_overlap:
                return self.maxClosed or other.minClosed
            else:
                return self.maxClosed != other.minClosed
        elif self.min == other.max:
            if allow_overlap:
                return self.minClosed or other.maxClosed
            else:
                return self.minClosed != other.maxClosed
        else: return False

    #-------- Factories ------------------------------------------------------

    @classmethod
    def open(cls, a, b):
        '''Return the open Range of all values between C{a} and C{b}.'''
        return cls(a, b, False, False)

    @classmethod
    def closed(cls, a, b):
        '''Return the closed Range of all values between C{a} and C{b}.'''
        return cls(a, b, True, True)

    @classmethod
    def openClosed(cls, a, b):
        '''Return the open-closed Range of all values between C{a} and C{b}.'''
        return cls(a, b, False, True)

    @classmethod
    def closedOpen(cls, a, b):
        '''Return the closed-open Range of all values between C{a} and C{b}.'''
        return cls(a, b, True, False)

    @classmethod
    def lessThan(cls, n, or_equal=False):
        '''Return the Range of all values less than and/or equal to C{n}.

        @param or_equal: If True, the lower bound is included in the Range.
        @type or_equal: bool
        '''
        return cls(None, n, False, or_equal)

    @classmethod
    def greaterThan(cls, n, or_equal=False):
        '''Return the Range of all values more than and/or equal to C{n}.

        @param or_equal: If True, the lower bound is included in the Range.
        @type or_equal: bool
        '''
        return cls(n, None, or_equal, False)

    @classmethod
    def singleton(cls, n):
        '''Return the Range consisting of a single value.'''
        return cls(n, n, True, True)

    @classmethod
    def empty(cls):
        '''Return the empty Range.'''
        return cls(0, 0, False, False)

    @classmethod
    def full(cls):
        '''Return the maximal unbounded Range.'''
        return cls(None, None, False, False)

#======= RangeSet ============================================================

class RangeSet(object):
    '''A set of L{Ranges <Range>}.

    RangeSets complements the standard discrete finite sets, available in
    python since 2.3. A RangeSet can be bounded or unbounded, contiguous or
    non-contiguous.

    @group Set operators: __invert__, __and__, __or__, __add__, __sub__, __xor__
    @group Subset, superset and equality predicates: issubset, __le__, __lt__,
        issuperset, __ge__, __gt__, __eq__, __ne__
    @group Other predicates: __contains__, __nonzero__, overlaps
    @group Factories: fromIterable, open, closed, openClosed, closedOpen,
        lessThan, greaterThan, singleton, allExcept, empty, full
    '''

#   - __init__, __iter__
#   - __or__, __and__, __xor__, __sub__, __invert__

    def __init__(self, *args):
        '''Create a RangeSet from zero or more Ranges, other RangeSets,
        iterables and atomic values.

        If no parameters are provided, the empty RangeSet is constructed.
        Otherwise, the RangeSet is formed as the union of the Ranges,
        RangeSets, iterable elements and atomic parameters:
            >>> print RangeSet(Range.open(4,6), xrange(1,6), -1,
                               Range.lessThan(-2))
            RangeSet((-oo,-2), {-1}, {1}, {2], {3}, [4,6))
        '''
        self._ranges = []
        for arg in args:
            if isinstance(arg,RangeSet):
                for subrange in arg:
                    pass
            elif isinstance(arg,Range):
                pass
            elif isatomic(arg):
                pass
            else:
                for i in arg:
                    pass


    def _addRange(self, r):
        if r:   # Don't bother appending an empty Interval
            # If r continuously joins with any of the other
            newRanges = []
            for subrange in self._ranges:
                if subrange.overlaps(r) or subrange.adjacentTo(r):
                    r = r + i
                else:
                    newRanges.append(subrange)
            newRanges.append(r)
            self.intervals = newIntervals

    #-------- factories ------------------------------------------------------

    @classmethod
    def fromIterable(cls, iterable):
        '''Return a RangeSet of all the values of an iterable.'''

    @classmethod
    def open(cls, a, b):
        return cls(cls._getRangeClass().open(a,b))

    @classmethod
    def closed(cls, a, b):
        return cls(cls._getRangeClass().closed(a,b))

    @classmethod
    def openClosed(cls, a, b):
        return cls(cls._getRangeClass().openClosed(a,b))

    @classmethod
    def closedOpen(cls, a, b):
        return cls(cls._getRangeClass().closedOpen(a,b))

    @classmethod
    def lessThan(cls, n, or_equal=False):
        return cls(cls._getRangeClass().lessThan(n,or_equal))

    @classmethod
    def greaterThan(cls, n, or_equal=False):
        return cls(cls._getRangeClass().greaterThan(n,or_equal))

    @classmethod
    def allExcept(cls, n):
        '''Return the RangeSet of all values except for C{n}.'''
        makeRange = cls._getRangeClass()
        return cls(makeRange.lessThan(n) | makeRange.greaterThan(n))

    @classmethod
    def singleton(cls, n):
        return cls(cls._getRangeClass().singleton(n))

    @classmethod
    def full(cls):
        return cls(cls._getRangeClass().full())

    @classmethod
    def empty(cls):
        '''Return the empty L{Range}.'''
        return cls(cls._getRangeClass().empty())

    @classmethod
    def _getRangeClass(cls):
        return Range

    #-------- Subset, superset and equality predicates -----------------------

    def issubset(self, other):
        '''Check if this RangeSet is a subset of C{other}.'''

    __le__ = issubset

    def issuperset(self, other):
        '''Check if this RangeSet is a superset of C{other}.'''

    __ge__ = issuperset

    def __eq__(self, other):
        '''Check if this two RangeSets are equal.'''

    #-------- Miscellaneous -----------------------------------------------
    def __iter__(self): pass
    def __repr__(self): pass
    __str__ = __repr__

    #-------- Other predicates -----------------------------------------------

    def __contains__(self, obj):
        '''Check if C{obj} is contained in this RangeSet.'''

    def __nonzero__(self):
        '''Check if this RangeSet is not empty.'''

    def overlaps(self, other):
        '''Check if this RangeSet overlaps with another RangeSet, Range or iterable.'''

    #-------- Set operators --------------------------------------------------

    def __or__(self, other): pass
    __add__ = __or__
    def __and__(self, other): pass
    def __xor__(self, other): pass
    def __sub__(self, other): pass
    def __invert__(self): pass


#    def __str__(self):
#        """
#        This function shows a string representation of a RangeSet.  The string
#        is shown sorted, with all intervals normalized.
#
#        """
#        if not self.intervals:
#            rangeStr = "<Empty>"
#        else:
#            rangeStr = ",".join(str(r) for r in sorted(self.intervals))
#        return "RangeSet: " + rangeStr
#
#    def __contains__(self, obj):
#        """
#        Returns True if obj is a subset of self.
#
#        >>> empty = RangeSet()
#        >>> all = RangeSet(Range(None, False, None, False))
#        >>> some = RangeSet(
#        ...   2, 8, Range(12, True, 17, False),
#        ...   Range(17, False, None, False))
#        >>> 17 in empty
#        False
#        >>> 17 in all
#        True
#        >>> 17 in some
#        False
#        >>> r = Range(100, True, 400, False)
#        >>> r in empty
#        False
#        >>> r in all
#        True
#        >>> r in some
#        True
#        >>> empty in all
#        False
#        >>> empty in some
#        False
#        >>> all in empty
#        False
#        >>> all in some
#        False
#        >>> some in empty
#        False
#        >>> some in all
#        True
#        """
#        if obj.__class__ == RangeSet:
#            if len(obj.intervals) == 0:
#                result = False
#            else:
#                result = True
#                for i in obj.intervals:
#                    if i not in self:
#                        result = False
#                        break
#        else:
#            result = False
#            for r in self.intervals:
#                if obj in r:
#                    result = True
#                    break
#        return result
#
#    def __sub__(self, other):
#        """
#        Returns all values of self minus all matching values in other.
#
#        >>> empty     = RangeSet()
#        >>> all       = RangeSet(Range(None, False, None, False))
#        >>> negatives = RangeSet(Range(None, False, 0, False))
#        >>> positives = RangeSet(Range(0, False, None, False))
#        >>> naturals  = RangeSet(Range(0, True,  None, False))
#        >>> evens     = RangeSet(-8, -6, -4, -2, 0, 2, 4, 6, 8)
#        >>> zero      = RangeSet(0)
#        >>> nonzero   = ne(0)
#        >>> print evens - nonzero
#        RangeSet: 0
#        >>> print empty - naturals
#        RangeSet: <Empty>
#        >>> print zero - naturals
#        RangeSet: <Empty>
#        >>> print positives - zero
#        RangeSet: (0,~)
#        >>> print naturals - negatives
#        RangeSet: [0,~)
#        >>> print all - zero
#        RangeSet: (-~,0),(0,~)
#        >>> all - zero == nonzero
#        True
#        >>> print evens - set((2, 4, 6, 8))
#        RangeSet: -8,-6,-4,-2,0
#        >>> print evens - 8
#        RangeSet: -8,-6,-4,-2,0,2,4,6
#        >>> print le(40) - 40
#        RangeSet: (-~,40)
#        """
#        if other.__class__ == RangeSet:
#            result = copy.deepcopy(self)
#            for j in other.intervals:
#                temp = RangeSet()
#                for i in result.intervals:
#                    if i.overlaps(j):
#                        if i in j:
#                            pass
#                        elif j in i:
#                            if j.min != None:
#                                temp.append(Range(
#                                    i.min, i.linc, j.min, not j.linc))
#                            if j.max != None:
#                                temp.append(Range(
#                                    j.max, not j.uinc, i.max, i.uinc))
#                        elif j < i:
#                            temp.append(Range(
#                                j.max, not j.uinc, i.max, i.uinc))
#                        else:
#                            temp.append(Range(
#                                i.min, i.linc, j.min, not j.linc))
#                    else:
#                        temp.append(copy.deepcopy(i))
#                result = temp
#        else:
#            result = self - RangeSet(other)
#        return result
#
#
#    def __and__(self, other):
#        """
#        This function returns the intersection of self and other.
#
#        >>> empty     = RangeSet()
#        >>> negatives = RangeSet(Range(None, False, 0, False))
#        >>> positives = RangeSet(Range(0, False, None, False))
#        >>> naturals  = RangeSet(Range(0, True,  None, False))
#        >>> evens     = RangeSet(-8, -6, -4, -2, 0, 2, 4, 6, 8)
#        >>> zero      = RangeSet(0)
#        >>> nonzero   = ne(0)
#        >>> print naturals and naturals
#        RangeSet: [0,~)
#        >>> print evens & zero
#        RangeSet: 0
#        >>> print negatives & zero
#        RangeSet: <Empty>
#        >>> print nonzero & positives
#        RangeSet: (0,~)
#        >>> print empty & zero
#        RangeSet: <Empty>
#        >>> print evens & set((4, -2, 0, 3))
#        RangeSet: -2,0,4
#        >>> print evens & 5
#        RangeSet: <Empty>
#        >>> print evens & 2
#        RangeSet: 2
#        """
#        if other.__class__ == RangeSet:
#            result = RangeSet()
#            for j in other.intervals:
#                for i in self.intervals:
#                    if i.overlaps(j):
#                        if i in j:
#                            result.append(copy.deepcopy(i))
#                        elif j in i:
#                            result.append(copy.deepcopy(j))
#                        elif j < i:
#                            result.append(
#                                Range(i.min, i.linc, j.max, j.uinc))
#                        else:
#                            result.append(
#                                Range(j.min, j.linc, i.max, i.uinc))
#        else:
#            result = self & RangeSet(other)
#        return result
#
#    def __or__(self, other):
#        """
#        This function returns the union of two RangeSets.  It does the same
#        thing as the __add__ function.  It can also accept sets or single
#        values.
#
#        >>> empty     = RangeSet()
#        >>> negatives = RangeSet(Range(None, False, 0, False))
#        >>> positives = RangeSet(Range(0, False, None, False))
#        >>> naturals  = RangeSet(Range(0, True,  None, False))
#        >>> evens     = RangeSet(-8, -6, -4, -2, 0, 2, 4, 6, 8)
#        >>> zero      = RangeSet(0)
#        >>> nonzero   = ne(0)
#        >>> print evens | positives
#        RangeSet: -8,-6,-4,-2,[0,~)
#        >>> print negatives | zero
#        RangeSet: (-~,0]
#        >>> print empty | negatives
#        RangeSet: (-~,0)
#        >>> print empty | naturals
#        RangeSet: [0,~)
#        >>> print nonzero | evens
#        RangeSet: (-~,~)
#        >>> print evens | set((-3, -5))
#        RangeSet: -8,-6,-5,-4,-3,-2,0,2,4,6,8
#        >>> print nonzero | 0 == all
#        True
#        """
#        if other.__class__ == RangeSet:
#            union = copy.deepcopy(self)
#            for r in other.intervals:
#                union.append(copy.deepcopy(r))
#        else:
#            union = self | RangeSet(other)
#        return union
#
#    def __xor__(self, other):
#        """
#        This function returns the exclusive or of two RangeSets.  Regular sets
#    or single values can also be xor'ed.
#
#        >>> empty     = RangeSet()
#        >>> negatives = RangeSet(Range(None, False, 0, False))
#        >>> positives = RangeSet(Range(0, False, None, False))
#        >>> naturals  = RangeSet(Range(0, True,  None, False))
#        >>> evens     = RangeSet(-8, -6, -4, -2, 0, 2, 4, 6, 8)
#        >>> zero      = RangeSet(0)
#        >>> nonzero   = ne(0)
#        >>> print nonzero ^ naturals
#        RangeSet: (-~,0]
#        >>> print zero ^ negatives
#        RangeSet: (-~,0]
#        >>> print positives ^ empty
#        RangeSet: (0,~)
#        >>> print evens ^ zero
#        RangeSet: -8,-6,-4,-2,2,4,6,8
#        >>> print evens ^ set((2, 4, 6, 8, 10))
#        RangeSet: -8,-6,-4,-2,0,10
#        >>> print zero ^ 0
#        RangeSet: <Empty>
#        >>> print zero ^ 42
#        RangeSet: 0,42
#        """
#        return (self | other) - (self & other)
#
#    def __invert__(self):
#        """
#        This function returns the disjoint set of self.  In other words,
#        all values self doesn't include are in the returned set.
#
#        >>> empty     = RangeSet()
#        >>> negatives = RangeSet(Range(None, False, 0, False))
#        >>> positives = RangeSet(Range(0, False, None, False))
#        >>> naturals  = RangeSet(Range(0, True,  None, False))
#        >>> evens     = RangeSet(-8, -6, -4, -2, 0, 2, 4, 6, 8)
#        >>> zero      = RangeSet(0)
#        >>> nonzero   = ne(0)
#        >>> print ~empty
#        RangeSet: (-~,~)
#        >>> ~negatives == naturals
#        True
#        >>> print ~positives
#        RangeSet: (-~,0]
#        >>> ~naturals == negatives
#        True
#        >>> print ~evens
#        RangeSet: (-~,-8),(-8,-6),(-6,-4),(-4,-2),(-2,0),(0,2),(2,4),(4,6),(6,8),(8,~)
#        >>> ~zero == nonzero
#        True
#        >>> ~nonzero == zero
#        True
#        """
#        return RangeSet(Range(None, False, None, False)) - self
#
#    def __eq__(self, other):
#        """
#        Two RangeSets are identical if they contain the exact same sets.  Note
#        that an empty set is never equal to any other set, even an empty
#        one.
#
#        >>> RangeSet(4) == RangeSet(1)
#        False
#        >>> RangeSet(5) == RangeSet(5)
#        True
#        >>> s1 = RangeSet(Range(4, True, 7, True))
#        >>> s2 = RangeSet(Range(4, True, 7, False))
#        >>> s1 == s2
#        False
#        >>> s2.append(7)
#        >>> s1 == s2
#        True
#        """
#        return (self in other) and (other in self)
#
#    def __nonzero__(self):
#        """
#        An empty RangeSet is the zero-like value.
#
#        >>> empty = RangeSet()
#        >>> nonempty = RangeSet(3)
#        >>> if empty:
#        ...     print "Non-empty"
#        >>> if nonempty:
#        ...     print "Non-empty"
#        Non-empty
#        """
#        return (len(self.intervals) > 0)
#
#    def append(self, obj):
#        """
#        This function adds a Range, discrete, or RangeSet to a RangeSet.
#
#        >>> r = RangeSet()
#        >>> r.append(4)
#        >>> print r
#        RangeSet: 4
#        >>> r.append(Range(23, False, 39, True))
#        >>> print r
#        RangeSet: 4,(23,39]
#        >>> r.append(Range(None, False, 25, False))
#        >>> print r
#        RangeSet: (-~,39]
#        >>> r2 = RangeSet(Range(None, False, None, False))
#        >>> r.append(r2)
#        >>> print r
#        RangeSet: (-~,~)
#        """
#        if obj.__class__ == RangeSet:
#            for r in obj.intervals:
#                self.append(r)
#        else:
#            if obj.__class__ == Range:
#                r = obj
#            else:
#                r = Range(obj, True, obj, True)
#
#            if r:   # Don't bother appending an empty Range
#                # If r continuously joins with any of the other
#                newRanges = []
#                for i in self.intervals:
#                    if i.overlaps(r) or i.adjacentTo(r):
#                        r = r + i
#                    else:
#                        newRanges.append(i)
#                newRanges.append(r)
#                self.intervals = newRanges


#        if other.__class__ == RangeSet:
#            union = copy.deepcopy(self)
#            for r in other.intervals:
#                union.append(copy.deepcopy(r))
#        else:
#            union = self | RangeSet(other)
#        return union


    #def __add__(self, other):
    #    """
    #    Yields a Range that encompasses self and other.  If the Ranges don't
    #    overlap, then an exception is raised.
    #        >>> r1  = Range(None, False, -100, False)
    #        >>> r2  = Range(None, False, -100, True)
    #        >>> r3  = Range(None, False,  100, False)
    #        >>> r4  = Range(None, False,  100, True)
    #        >>> r5  = Range(None, False, None, False)
    #        >>> r6  = Range(-100, False,  100, False)
    #        >>> r7  = Range(-100, False,  100, True)
    #        >>> r8  = Range(-100, False, None, False)
    #        >>> r9  = Range(-100, True,  -100, True)
    #        >>> r10 = Range(-100, True,   100, False)
    #        >>> r11 = Range(-100, True,   100, True)
    #        >>> r12 = Range(-100, True,  None, False)
    #        >>> r13 = Range( 100, False, None, False)
    #        >>> r14 = Range( 100, True,   100, True)
    #        >>> r15 = Range( 100, True,  None, False)
    #        >>> print r4 + r9
    #        (-~,100]
    #        >>> print r1 + r10
    #        (-~,100)
    #        >>> print r8 + r15
    #        (-100,~)
    #        >>> print r13 + r15
    #        [100,~)
    #        >>> print r7 + r11
    #        [-100,100]
    #        >>> print r12 + r15
    #        [-100,~)
    #        >>> print r2 + r13
    #        Traceback (most recent call last):
    #            ...
    #        ArithmeticError: The Ranges are disjoint.
    #        >>> print r5 + r6
    #        (-~,~)
    #        >>> print r5 + r14
    #        (-~,~)
    #        >>> print r3 + r4
    #        (-~,100]
    #    """
    #    if self.overlaps(other) or self.adjacentTo(other):
    #        if self.min == None or other.min == None:
    #            min = None
    #            linc = False
    #        elif self.min < other.min:
    #            min = self.min
    #            linc = self.linc
    #        elif self.min == other.min:
    #            min = self.min
    #            linc = max(self.linc, other.linc)
    #        else:
    #            min = other.min
    #            linc = other.linc
    #
    #        if self.max == None or other.max == None:
    #            max = None
    #            uinc = False
    #        elif self.max > other.max:
    #            max = self.max
    #            uinc = self.uinc
    #        elif self.max == other.max:
    #            max = self.max
    #            uinc = max(self.uinc, other.uinc)
    #        else:
    #            max = other.max
    #            uinc = other.uinc
    #        return Range(min, linc, max, uinc)
    #    else:
    #        raise ArithmeticError('The Ranges are disjoint.')

#======= module privates =====================================================

class _Smallest(object):
    def __cmp__(self, other): return self is not other and -1 or 0
    def __repr__(self): return '-oo'
_Smallest = _Smallest()

class _Largest(object):
    def __cmp__(self, other): return self is not other and 1 or 0
    def __repr__(self): return 'oo'
_Largest = _Largest()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
