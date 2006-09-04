from itertools import izip,imap,starmap,islice
from operator import sub,and_

def difs_reduce(seq):
    differences = []
    def neighborDifference(left, right, accum=differences.append):
        accum(right - left)
        return right
    reduce(neighborDifference, seq)
    return differences

def difs_zip(seq):
    return starmap(sub, zip(seq[1:],seq))    

def difs_izip(seq):
    return starmap(sub, izip(islice(seq,1,None),seq))

def window_by_two(iterable):
        it = iter(iterable)
        cur = it.next()
        for next in it:
                yield next,cur
                cur = next

def difs_wib(seq, wib=window_by_two):
    return starmap(sub, wib(seq))

def difs_loop(seq):
    differences = []
    it = iter(seq)
    a = it.next()
    for b in it:
        differences.append(b-a)
        a = b
    return differences


def difs_imap(seq):
    return imap(sub, seq[1:], seq[:-1])

_sub = lambda seq: lambda i: seq[i+1] - seq[i]
def difs_xrange(seq):
    sub = _sub(seq)
    return imap(sub,xrange(len(seq)-1))
    
#print list(difs_izip(range(100)))    
#print list(difs_xrange(range(100))) == list(difs_izip(range(100)))

if __name__ == '__main__':
    import psyco; psyco.full()
    import timeit
    funs = 'wib izip imap xrange '.split() #loop zip reduce
    test = lambda f: list(f(range(999)))
    assert reduce(and_, [test(difs_wib) == test(f)
                         for f in difs_izip,difs_xrange,difs_imap,
                                  difs_loop, difs_zip, difs_reduce])
    bargs = ['-c', '-simport loop_bench', '-sx=range(100)'] #'-sx=[bench.Point(1,2)]*1000']
    #funs = 'izip map'.split()
    for fun in funs:
        args = bargs + ['loop_bench.difs_%s(x)' % fun]
        print '%8s:' % fun,
        timeit.main(args)
