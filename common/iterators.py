from itertools import *

def take(n, seq):
    return list(islice(seq, n))

def enumerate(iterable):
    return izip(count(), iterable)

def tabulate(function):
    "Return function(0), function(1), ..."
    return imap(function, count())

def iteritems(mapping):
    return izip(mapping.iterkeys(), mapping.itervalues())

def nth(iterable, n):
    "Returns the nth item"
    return list(islice(iterable, n, n+1))

def all(seq, pred=bool):
    "Returns True if pred(x) is True for every element in the iterable"
    return False not in imap(pred, seq)

def any(seq, pred=bool):
    "Returns True if pred(x) is True at least one element in the iterable"
    return True in imap(pred, seq)

def no(seq, pred=bool):
    "Returns True if pred(x) is False for every element in the iterable"
    return True not in imap(pred, seq)

def quantify(seq, pred=bool):
    "Count how many times the predicate is True in the sequence"
    return sum(imap(pred, seq))

def padnone(seq):
    "Returns the sequence elements and then returns None indefinitely"
    return chain(seq, repeat(None))

def ncycles(seq, n):
    "Returns the sequence elements n times"
    return chain(*repeat(seq, n))

def dotproduct(vec1, vec2):
    return sum(imap(operator.mul, vec1, vec2))

def window(seq, n=2):
    "Returns a sliding window (of width n) over data from the iterable"
    "   s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...                   "
    it = iter(seq)
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result

def tee(iterable):
    "Return two independent iterators from a single iterable"
    def gen(next, data={}, cnt=[0]):
        dpop = data.pop
        for i in count():
            if i == cnt[0]:
                item = data[i] = next()
                cnt[0] += 1
            else:
                item = dpop(i)
            yield item
    next = iter(iterable).next
    return (gen(next), gen(next))
