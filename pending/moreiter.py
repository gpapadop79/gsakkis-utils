from collections import deque
from itertools import chain,tee,cycle,islice
from heapq import heapify, heappop, heapreplace
try: frozenset
except NameError:
    from sets import ImmutableSet as frozenset

def cyclefrom(iterable, start=0):
    """Cycle over the elements of the iterable starting at the given position.

    >>> from itertools import islice
    >>> list(islice(cyclefrom('abcde', 3), 9))
    ['d', 'e', 'a', 'b', 'c', 'd', 'e', 'a', 'b']
    >>> list(islice(cyclefrom('abcde', 5), 9))
    ['a', 'b', 'c', 'd', 'e', 'a', 'b', 'c', 'd']
    """
    # chain the last part (iterable[:start]) with the first (iterable[:start])
    # and cycle over it. Needs to replicate the iterable for consuming each part
    it1,it2 = tee(iterable)
    return cycle(chain(islice(it1, start, None), islice(it2, start)))

def itermerge(*iterables):
    '''Return an iterator that yields all the items of the given sorted
    iterables in ascending order.

    >>> s1 = [10, 20, 39, 40, 50]
    >>> s2 = [15, 18]
    >>> s3 = [17, 27, 37]
    >>> list(itermerge(s1, s2, s3))
    [10, 15, 17, 18, 20, 27, 37, 39, 40, 50]
    '''
    pqueue = []
    for i in map(iter, iterables):
        try:
            pqueue.append((i.next(), i.next))
        except StopIteration:
            pass
    heapify(pqueue)
    while pqueue:
        val, it = pqueue[0]
        yield val
        try:
            heapreplace(pqueue, (it(), it))
        except StopIteration:
            heappop(pqueue)


def cartesian_product(*sequences):
    '''
    >>> for x in cartesian_product(range(3), 'a', (3.25,-1.2)):
    ...     print x
    (0, 'a', 3.25)
    (0, 'a', -1.2)
    (1, 'a', 3.25)
    (1, 'a', -1.2)
    (2, 'a', 3.25)
    (2, 'a', -1.2)
    '''
    if not sequences:
        yield ()
    else:
        for item in sequences[0]:
            head = (item,)
            for tail in cartesian_product(*sequences[1:]):
                yield head + tail


def powerset(iterable):
    '''
    >>> for s in powerset('abc'):
    ...     print s
    frozenset([])
    frozenset(['a'])
    frozenset(['b'])
    frozenset(['a', 'b'])
    frozenset(['c'])
    frozenset(['a', 'c'])
    frozenset(['c', 'b'])
    frozenset(['a', 'c', 'b'])
    '''
    yield frozenset()
    for s in _powerset(iter(iterable)):
        yield s


def _powerset(iterator):
    first = frozenset([iterator.next()])
    yield first
    for s in _powerset(iterator):
        yield s
        yield s | first



def interleave(*iterables):
    """
    >>> it = interleave("abc","12345","XY")
    >>> list(it)
    ['a', '1', 'X', 'b', '2', 'Y', 'c', '3', '4', '5']
    >>> list(it)
    []
    """
    iters = deque(map(iter, iterables))
    while iters:
        it = iters.popleft()
        try:
            next = it.next()
        except StopIteration:
            continue
        else:
            iters.append(it)
            yield next


class Interleave(object):
    """Iterator that cycles over one or more iterables, yielding one item from
    each iterable at a time. Once an iterable is exhausted, it is removed from
    the cycle. This iterator is exhausted when all participating iterables are
    exhausted.

    >>> it = Interleave("abc","12345","XY")
    >>> list(it)
    ['a', '1', 'X', 'b', '2', 'Y', 'c', '3', '4', '5']
    >>> list(it)
    []
    """

    def __init__(self, *iterables):
        iters = self.__iters = deque(map(iter, iterables))
        def generator():
            while iters:
                it = iters.popleft()
                try:
                    next = it.next()
                except StopIteration:
                    continue
                else:
                    iters.append(it)
                    yield next
        self.__this_iter = generator()

    def append(self,iterable):
        """Adds an iterable to the existing cycle of iterables.

        The given iterable is added in front of the current position in the
        cycle so that it's called only after all the others.

        >>> example = Interleave("abc", "12345")
        >>> [example.next() for i in range(3)]
        ['a', '1', 'b']
        >>> example.append("XY")
        >>> list(example)
        ['2', 'c', 'X', '3', 'Y', '4', '5']
        """
        self.__iters.append(iter(iterable))

    def __iter__(self):
        return self

    def next(self):
        return self.__this_iter.next()


def iterCombinations_1(length,seq):
    if length:
        for rest in iterCombinations_1(length-1, seq):
            for item in seq:
                yield [item] + rest
    else:
        yield []


def iterCombinations_2(length,seq):
    return _iterCombinations_2(seq, 0, [None]*length)

def _iterCombinations_2(seq, index, result):
    if index < len(result):
        for rest in _iterCombinations_2(seq, index+1, result):
            for item in seq:
                result[index] = item
                yield result
    else:
        yield result


def test_itercomb():
    import timeit
    for f in iterCombinations_1,iterCombinations_2:
        name = f.__name__
        timer = timeit.Timer("%s(100, range(10))" % name,
                           "from spam import %s" % name)
        #print name, min(timer.repeat(3,100000))



class SequenceIterator(object):
    def __init__(self, seq):
        if not hasattr(seq,'__getitem__'):
            raise TypeError, "Sequence type required"
        self._seq = seq
        self._pos = -1

    def __iter__(self):
        return self

    def reversed(self):
        while True:
            try: yield self.previous()
            except StopIteration: break

    def next(self):
        try:
            pos = self._pos + 1
            result = self._seq[pos]
            self._pos = pos
        except IndexError:
            raise StopIteration
        return result

    def previous(self):
        pos = self._pos - 1
        if pos < 0:
            raise StopIteration
        result = self._seq[pos]
        self._pos = pos
        return result

class ListIter(object):

    def __init__(self, lst):
        self._lst = lst
        self._next = 0
        self._canRemove = False

    def __iter__(self):
        return self

    def next(self):
        cur = self._next
        self._next += 1
        try: next = self._lst[cur]
        except IndexError:
            raise StopIteration()
        else:
            self._canRemove = True
            return next

    def remove(self):
        if self._canRemove:
            self._next -= 1
            removed = self._lst.pop(self._next)
            self._canRemove = False
            return removed
        else:
            raise RuntimeError("Current item has already been removed")

def test_listiter():
    z = range(10)
    it = ListIter(z)
    for x in it:
        if x % 2 == 1:
            print "removed", it.remove()
    assert z == [0,2,4,6,8]


def finditer(self, sub, *startend):
    start,end = 0,len(self)
    numargs = len(startend)
    if numargs:
        start = startend[0]
        if numargs > 1:
            end = startend[1]
            if numargs > 2:
                raise TypeError('finditer() takes at most 3 arguments '
                                '(%d given)' % (numargs+1))
    while True:
        index = self.find(sub,start,end)
        if index > 0:
            yield index
            start = index +1
        else:
            break


if __name__ == '__main__':
    import doctest
    doctest.testmod()
