import random
import py.test
import math, operator

import datastructs.heap as heap



#==== Test default Heap ======================================================

class TestHeap(object):

    key = None

    #--- helpers -------------------------------------------------------------

    def makeHeap(self, iterable=(), key=None):
        return heap.Heap(iterable, key or self.key)

    def sorted(self, iterable, key=None):
        return sorted(iterable, key=key or self.key)

    def min(self, iterable, key=None):
        key = key or self.key
        if key is None:
            return min(iterable)
        return min((key(x),x) for x in iterable)[1]

    def assert_heap_invariant(self, heap):
        # Check the heap invariant
        key = self.key or (lambda x:x)
        for pos, item in enumerate(heap):
            if pos: # pos 0 has no parent
                parentpos = (pos-1) >> 1
                assert key(heap[parentpos]) <= key(item)

    #--- tests ---------------------------------------------------------------

    def test_push_pop(self):
        # push 256 random numbers and pop them off, verifying all's OK.
        heap = self.makeHeap()
        data = []
        self.assert_heap_invariant(heap)
        for _ in xrange(256):
            item = random.random()
            data.append(item)
            heap.push(item)
            self.assert_heap_invariant(heap)
        results = []
        while heap:
            item = heap.popmin()
            self.assert_heap_invariant(heap)
            results.append(item)
        assert self.sorted(data) == results
        # check that the invariant holds for a sorted array
        self.assert_heap_invariant(results)
        py.test.raises(TypeError, heap.push)
        py.test.raises(TypeError, heap.push, None, None)
        py.test.raises(TypeError, heap.popmin, None)

    def test_heapify(self):
        for size in xrange(30):
            heap = self.makeHeap([random.random() for dummy in xrange(size)])
            self.assert_heap_invariant(heap)
        py.test.raises(TypeError, self.makeHeap, None)

    def test_replace(self):
        heap = self.makeHeap([16,12,18,15])
        m = self.min(heap); assert heap.replace(13) == m; assert 13 in heap
        m = self.min(heap); assert heap.pushpop(17) == m; assert 17 in heap
        assert self.makeHeap().pushpop(4) == 4
        py.test.raises(TypeError, heap.replace, None, None)
        # replace fails on an empty heap
        py.test.raises(IndexError, self.makeHeap().replace, 1)

    def test_naive_nbest(self):
        data = [random.randrange(2000) for _ in xrange(1000)]
        heap = self.makeHeap()
        for item in data:
            heap.push(item)
            if len(heap) > 10:
                heap.popmin()
        assert list(heap.iterpop()) == self.sorted(data)[-10:]

    def test_nbest(self):
        # Less-naive "N-best" algorithm, much faster (if len(data) is big
        # enough <wink>) than sorting all of data.  However, if we had a max
        # heap instead of a min heap, it could go faster still via
        # heapify'ing all of data (linear time), then doing 10 heappops
        # (10 log-time steps).
        data = [random.randrange(2000) for _ in xrange(1000)]
        heap = self.makeHeap(data[:10])
        key = self.key or (lambda x:x)
        for item in data[10:]:
            if key(item) > key(heap[0]):  # this gets rarer the longer we run
                heap.replace(item)
        assert list(heap.iterpop()) == self.sorted(data)[-10:]

    def test_heapsort(self):
        # Exercise everything with repeated heapsort checks
        for trial in xrange(100):
            size = random.randrange(50)
            data = [random.randrange(25) for _ in xrange(size)]
            if trial & 1:     # Half of the time, use heapify
                heap = self.makeHeap(data)
            else:             # The rest of the time, use heappush
                heap = self.makeHeap()
                for item in data:
                    heap.push(item)
            heap_sorted = [heap.popmin() for _ in xrange(size)]
            assert heap_sorted == self.sorted(data)

    def test_iterpop(self):
        data = [random.randrange(2000) for _ in xrange(100)]
        iterpop = self.makeHeap(data).iterpop()
        assert iter(iterpop) is iterpop
        for i,j in zip(iterpop, self.sorted(data)):
            assert i == j
        py.test.raises(StopIteration, iterpop.next)

    def test_getitem(self):
        heap= self.makeHeap([random.randrange(200) for _ in xrange(100)])
        for slicedheap in heap[:10], heap[-10:], heap[10:20]:
            self.assert_heap_invariant(slicedheap)
        py.test.raises(IndexError, heap.__getitem__, len(heap))
        py.test.raises(IndexError, heap.__getitem__, -len(heap)-1)

    def test_setitem(self):
        data = [random.randrange(200) for _ in xrange(100)]
        heap = self.makeHeap(data)
        indices = [random.randrange(len(heap)) for _ in xrange(100)]
        for index in indices:
            value = heap[index]
            newvalue = value + random.randrange(-10,11)
            data.remove(value); data.append(newvalue)
            heap[index] = newvalue
            self.assert_heap_invariant(heap)
        assert list(heap.iterpop()) == self.sorted(data)

    def test_delitem(self):
        data = [random.randrange(200) for _ in xrange(100)]
        heap = self.makeHeap(data)
        while heap:
            index = random.randrange(len(heap))
            value = heap.pop(index)
            data.remove(value)
            self.assert_heap_invariant(heap)
        assert list(heap.iterpop()) == self.sorted(data)

    def test_iter(self):
        heap = self.makeHeap([random.randrange(200) for _ in xrange(100)])
        assert self.sorted(list(heap)) == list(heap.iterpop())

    def test_index(self):
        data = [random.randrange(200) for _ in xrange(100)]
        heap = self.makeHeap(data)
        for i in [random.randrange(-len(heap),len(heap)) for _ in xrange(100)]:
            item = heap[i]
            firstIndex = heap.index(item)
            assert heap[firstIndex] == item
            if i < 0:
                i += len(heap)
            assert firstIndex <= i
        py.test.raises(ValueError, heap.index, "a")

    def test_remove(self):
        data = [random.randrange(200) for _ in xrange(100)]
        heap = self.makeHeap(data)
        while heap:
            i = random.randrange(-len(heap),len(heap))
            heap.remove(heap[i])
            self.assert_heap_invariant(heap)
        py.test.raises(ValueError, heap.remove, "a")

    def test_extend(self):
        data = [random.randrange(200) for _ in xrange(100)]
        heap = self.makeHeap(data)
        for i in xrange(10):
            new = [random.randrange(200) for _ in xrange(random.randrange(20))]
            data.extend(new)
            heap.extend(new)
            self.assert_heap_invariant(heap)
        assert list(heap.iterpop()) == self.sorted(data)

    def test_sort(self):
        data = [random.randrange(200) for _ in xrange(100)]
        heap = self.makeHeap(data)
        heap.sort()
        self.assert_heap_invariant(heap)
        assert list(heap) == self.sorted(data)

    def test_pop(self):
        data = [random.randrange(200) for _ in xrange(100)]
        heap = self.makeHeap(data)
        # heap invariant is preserved after popping from the back
        while heap:
            heap.pop()
            self.assert_heap_invariant(heap)
        heap = self.makeHeap(data)
        while heap:
            i = random.randrange(-len(heap),len(heap))
            x = heap[i]
            assert heap.pop(i) == x
            self.assert_heap_invariant(heap)

    def test_cmp(self):
        data = [random.randrange(200) for _ in xrange(10)]
        heap = self.makeHeap(data)
        assert heap != data
        # a heap with the same data and a different key that preserves order
        # is equal; otherwise it is not
        if self.key:
            def preserve_order(x): return 2*self.key(x)
            def not_preserve_order(x): return math.sin(self.key(x))
        else:
            def preserve_order(x): return 2*x
            def not_preserve_order(x): return math.sin(x)
        assert heap == self.makeHeap(data, preserve_order)
        assert heap != self.makeHeap(data, not_preserve_order)
        # the order of pushing the data into the heap is significant, so the
        # following doesn't hold in general
        #assert heap == self.makeHeap(data[::-1])
        for stmt in 'heap < heap', 'heap <= heap','heap > heap','heap >= heap':
            exec ('try: %s\n'
                 'except TypeError: assert True\n'
                 'else: assert False') % stmt in locals()


#==== Test Heap with key =====================================================

class TestKeyHeap(TestHeap):

    key = operator.neg


if __name__ == '__main__':
    pass
