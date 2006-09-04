#!/usr/bin/env python

import threading
from math import sqrt

class PrimeFinder:
    def __init__(self, numthreads=1):
        self._numthreads = int(numthreads)

    def __call__(self, upto):
        upto = int(upto)
        lim = sqrt(upto)
        primes = (upto+1) * [1]
        nexti = _SafeCounter(2)
        def run():
            nk = 0
            while 1:
                k = nexti.postIncrement()
                if k > lim: break
                nk += 1
                if primes[k]:
                    r = upto / k
                    for i in range(2,r+1):
                        primes[i*k] = 0
            print "thread %s exiting; processed %d values of k" % (
                threading.currentThread().getName(), nk)
        workers = [threading.Thread(target=run, name="worker_%d" % i)
                   for i in xrange(self._numthreads)]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join()
        return [i for i,p in enumerate(primes) if (p and i>1)]

class _SafeCounter:
    def __init__(self,start=0):
        self._val = start
        self._lock = threading.Lock()

    def postIncrement(self, value=1):
        self._lock.acquire()
        old = self._val
        self._val += value
        self._lock.release()
        return old

    def preIncrement(self, value=1):
        self._lock.acquire()
        val = self._val = self._val + value
        self._lock.release()
        return val

def primeGenerator(upto=None):
    primes = []
    i = 2
    while True:
        if i > upto: raise StopIteration
        for p in primes:
            if i % p == 0:
                break
        else:
            primes.append(i)
            yield i
        i += 1


if __name__ == '__main__':
    import sys, sieve
    primes = PrimeFinder(sys.argv[2])(sys.argv[1])
    primes2 = sieve.findprimes(*sys.argv[1:])
    #primes3 = list(primeGenerator(int(sys.argv[1])))
    #for x in primeGenerator(int(sys.argv[1])):
    #    print x
    assert primes == primes2
    #print 'there are %d primes:' % len(primes)
