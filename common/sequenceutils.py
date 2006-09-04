'''Useful functions for iterable objects (such as lists and tuples).

@group Aggregating: sum, average, median, standardDeviation
@group Miscellaneous: sorted, uniq, groupBy, flatten
'''

#todo:
#? rewrite a cleaner unoptimized version of sorted / profile them
#? Optimize for Numeric arrays

import operator
from common.future import *

__author__ = "George Sakkis <gsakkis@rutgers.edu>"
__all__ = ["sum", "average", "median", "standardDeviation",
           "frequency", "uniq", "sorted", "groupBy", "flatten", "padfactory"]

##############################################################################

def sum(sequence, default=0):
    '''Return the sum of the items in sequence, or default for empty sequence.

    The objects in the sequence must support __add__.
    '''
    if sequence:
        return reduce(operator.add, sequence)
    return default

def average(sequence):
    '''Return the average (arithmetic mean) of the items in sequence.

    @param sequence: An iterable.
    @raise ZeroDivisionError: If the sequence is empty.
    '''
    return sum(sequence) / float(len(sequence))

def median(sequence, isSorted=True):
    '''Return the median of the items in sequence.

    The objects in the sequence must be comparable.

    @param sequence: An iterable.
    @param isSorted: Select True if the items are known to be sorted
        and False otherwise.
    '''
    if not isSorted:
        sequence = sorted(sequence)
    size = len(sequence)
    if size % 2 == 1:
        return sequence[(size-1)/2]
    else:
        return (sequence[(size-1)/2] + sequence[size/2]) / 2.0

def standardDeviation(sequence, isSample=True):
    '''Return the standard deviation of the items in sequence.

    @param sequence: An iterable.
    @param isSample: True if the elements in the sequence are assumed to
        be a sample of a larger population.
    @raise ZeroDivisionError: If the sequence is empty or if
        isSample and len(sequence)==1
    '''
    from math import sqrt
    m = average(sequence)
    try:
        # fast innerproduct if sequence is a Numeric array
        from Numeric import innerproduct
        diff = sequence - m
        s = innerproduct(diff,diff)
    except (ImportError,TypeError):
        #s = sum([(x-m)*(x-m) for x in sequence])
        s = 0
        for x in sequence:
            diff = x-m
            s += diff * diff
    # denominator is N-1 if isSample
    d = len(sequence) - bool(isSample)
    return sqrt(s / float(d))

def frequency(sequence):
    '''Return a dictionary that maps each item in sequence to its frequency.

    @param sequence: An iterable.
    '''
    freqMap = {}
    for item in sequence:
        freqMap[item] = freqMap.setdefault(item,0) + 1
    return freqMap

def uniq(sequence):
    '''Return a copy of the sequence without the duplicates.

    The order of the unique elements is preserved.

    @param sequence: An iterable.
    '''
    d = {}
    try:
        return [d.setdefault(i,i) for i in sequence if not d.has_key(i)]
    except TypeError:   # unhashable item(s)
        return [d.setdefault(repr(i),i)
                for i in sequence if not d.has_key(repr(i))]

def sorted(sequence, key=None, value=None, maxLength=None,
           descending=False, acceptTies=False, inPlace=False):
    '''Sort the sequence.

    @param sequence: An iterable.
    @param key: A callable f(item) that gives the key of the comparison;
        by default it is the item itself.
    @param value: A callable f(item) that gives the value to be kept for
        each item; by default it is the item itself.
    @param maxLength: If not None, return the top-N (or the last-N for
        descending) values.
    @param descending: True for ascending order, False for descending.
    @param acceptTies: if True, more than maxLength items may be returned
        if there are ties.
    @param inPlace: True if sequence is to be mutated as result of the call;
        False if a new sorted list is to be returned.
    '''
    if key is not None:
        if value is not None:
            newSequence = [(key(x),value(x)) for x in sequence]
        else:
            newSequence = [(key(x),x) for x in sequence]
    elif not inPlace:
        newSequence = [x for x in sequence]
    else:
        newSequence = sequence
    # works if sequence is a list (or a class that has a sort() method)
    try: newSequence.sort()
    except AttributeError:
        # otherwise make a list out of it
        newSequence = [x for x in newSequence]
        newSequence.sort()
    if descending:
        newSequence.reverse()
    if maxLength is not None:
        assert maxLength > 0
        # pick the first maxLength elements, or more if there are ties
        endIndex = maxLength
        if acceptTies:
            try:
                if key is None:
                    while newSequence[endIndex-1] == newSequence[endIndex]:
                        endIndex += 1
                else:
                    while newSequence[endIndex-1][0] == newSequence[endIndex][0]:
                        endIndex += 1
            except IndexError:
                pass
        newSequence = newSequence[:endIndex]
    if key is not None:
        newSequence = [v for k,v in newSequence]
    elif value is not None:
        assert key is None
        newSequence = [value(x) for x in newSequence]
    if inPlace:
        sequence[:] = newSequence
    return newSequence

def groupBy(sequence, key=None, value=None):
    '''Partition a sequence into groups.

    @param sequence: An iterable.
    @param key: A callable f(item) to be used as the partitioning key;
        by default it is the item itself.
    @param value: A callable f(item) that gives the value to be kept for
        each item; by default it is the item itself
    @return: A dict that maps each key to the list of values of the items
        in sequence that have this key (key : [values]).
    '''
    d = {}
    for item in sequence:
        if key is None: k = item
        else: k = key(item)
        if value is None: v = item
        else: v = value(item)
        d.setdefault(k, []).append(v)
    return d

def flatten(sequence):
    '''Flatten a (possibly nested) sequence.

    @param sequence: An iterable.
    '''
    if isinstance(sequence,basestring):
        return [sequence]
    try:
        return sum(map(flatten,sequence))
    except TypeError:
        return [sequence]


##############################################################################

def padfactory(minLength=0, defaults=(), extraItems=False):
    '''Return a function that can pad variable-length iterables.

    The returned function f:iterable -> iterable attempts to return an
    iterable of the same type as the original; if this fails it returns a list.

    @param minLength: The minimum required length of the iterable.
    @param defaults: A sequence of default values to pad shorter iterables.
    @param extraItems: Controls what to do with iterables longer than
        minlength + len(defaults).
            - If extraItems is None, the extra items are ignored.
            - else if bool(extraItems) is True, the extra items are packed in
              a tuple which is appended to the returned iterable. An empty
              tuple is appended if there are no extra items.
            - else a ValueError is thrown (longer iterables are not acceptable).
    '''
    # maximum sequence length (without considering extraItems)
    maxLength = minLength + len(defaults)
    from itertools import islice
    def closure(iterable):
        iterator = iter(iterable)   # make sure you can handle any iterable
        padded = list(islice(iterator,maxLength))
        if len(padded) < maxLength:
            # extend by the slice of the missing defaults
            for default in islice(defaults, len(padded) - minLength,
                                  maxLength - minLength):
                padded.append(default)
        if len(padded) < maxLength:
            raise ValueError("unpack iterable of smaller size")
        if extraItems:               # put the rest elements in a tuple
            padded.append(tuple(iterator))
        elif extraItems is None:     # silently ignore the rest of the iterable
            pass
        else:                        # should not have more elements
            try: iterator.next()
            except StopIteration: pass
            else: raise ValueError("unpack iterable of larger size")
        # try to return the same type as the original iterable;
        itype = type(iterable)
        if itype != list:
            try: padded = itype(padded)
            except TypeError: pass
        return padded
    return closure
