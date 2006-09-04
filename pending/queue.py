import sys

__author__ = "George Sakkis <gsakkis@rutgers.edu>"

#======= Queues ==============================================================

class Queue(object):
    def __init__(self, maxsize=sys.maxint):
        self._maxsize = maxsize

    def __len__(self):
        return len(self._container)

    def __iter__(self):
        return iter(self._container)

    def push(self,item):
        raise NotImplementedError

    def pop(self):
        raise NotImplementedError


class FIFOQueue(Queue):
    def __init__(self, maxsize=sys.maxint, containerclass=list):
        super(FIFOQueue,self).__init__(maxsize)
        self._container = containerclass()

    def push(self,item):
        # if the queue is full, discard any new item
        if len(self) < self._maxsize: self._container.append(item)

    def pop(self): return self._container.pop(0)


class RandomQueue(Queue):
    def __init__(self, maxsize=sys.maxint, containerclass=list):
        super(RandomQueue,self).__init__(maxsize)
        self._container = containerclass()

    def push(self,item):
        self._container.append(item)
        # if the queue is full, pop one item at random
        if len(self) == self._maxsize: self.pop()

    def pop(self):
        import random
        return self._container.pop(random.randrange(len(self)))


#======= Priority queues =====================================================

class PriorityQueue(Queue):
    def __init__(self, priorityFunction, maxsize=sys.maxint,
                 exceptionhandler=None):
        super(PriorityQueue,self).__init__(maxsize)
        self._priorityFunc = priorityFunction
        self._exceptionhandler = exceptionhandler


class ArrayPriorityQueue(PriorityQueue):
    def __init__(self, priorityFunction, maxsize=sys.maxint,
                 exceptionhandler=None):
        super(ArrayPriorityQueue,self).__init__(priorityFunction, maxsize,
                                                exceptionhandler)
        self._container = []

    def push(self, item):
        try:
            import bisect
            # insert the page with value the negative priority, so that pop
            # returns the minimum
            bisect.insort(self._container,(- self._priorityFunc(item), item))
            ##print  >> sys.stderr,item,"\tscore:",self.__priorityFunc(item)
            if len(self._container) == self._maxsize:  # remove last element
                self._container.pop()
        except:
            if self._exceptionhandler is not None:
                self._exceptionhandler(self,item)

    def pop(self):
        return self._container.pop(0)[1]


class HeapPriorityQueue(PriorityQueue):
    def __init__(self, priorityFunction, maxsize=sys.maxint,
                 exceptionhandler=None):
        super(HeapPriorityQueue,self).__init__(priorityFunction, maxsize,
                                               exceptionhandler)
        from priorityqueue import PriorityDictionary
        self._container = PriorityDictionary()

    def __iter__(self):
        return self._container.iterkeys()

    def push(self, item):
        # Caveat: If the queue is full, the last element should normally be
        # popped out, but the priorityQueue.PriorityDictionary can only return
        # the smallest() and not the largest() item
        if len(self) < self._maxsize:
            try:
                # insert the page with value the negative priority, so that
                # pop returns the minimum
                self._container[item] = - self._priorityFunc(item)
                #print  >> sys.stderr,item,"\tscore:",self._priorityFunc(item)
            except:
                if self._exceptionhandler is not None:
                    self._exceptionhandler(self,item)

    def pop(self):
        # pop and return a key with the minimum value
        smallest = self._container.smallest()
        del self._container[smallest]
        return smallest


if __name__ == '__main__':

    def testQueues(size, *queues):
        for item in xrange(size):
            for queue in queues:
                queue.push(item)
        import operator
        while reduce(operator.and_, map(len,queues)):
            for queue in queues: queue.pop()

    def testPriorityQueues(size, *queueclasses):
        f = lambda (k,v): v
        queues = [queueclass(priorityFunction=f) for queueclass in queueclasses]
        import random
        itemPriorityPairs = [ (i,10*random.random()) for i in xrange(size)]
        for item in itemPriorityPairs:
            for queue in queues:
                queue.push(item)
        import operator
        while reduce(operator.and_, map(len,queues)):
            assert reduce(operator.eq, [queue.pop() for queue in queues])

    def profiler(sizes, testFunc, args):
        for size in sizes:
            import profile, pstats
            code = "%s(%d,%s)" % (testFunc.__name__, size, args)
            print "Executing", code
            filename = 'profile_%d' % size
            profile.run(code,filename)
            s = pstats.Stats(filename)
            s.sort_stats("cumulative")
            s.print_stats("%s.*(push|pop)" % __file__)

    import inspect
    priorityQueueClasses = \
            [obj for (name,obj) in sys.modules[__name__].__dict__.items() \
                 if inspect.isclass(obj) and issubclass(obj,PriorityQueue) and obj != PriorityQueue]
    from linkedlist import LinkedList
    #profiler(map(int,sys.argv[1:]), testQueues, "FIFOQueue()")
    #profiler(map(int,sys.argv[1:]), testQueues, "FIFOQueue(containerclass=LinkedList)")
    #profiler(map(int,sys.argv[1:]), testQueues, "RandomQueue()")
    #profiler(map(int,sys.argv[1:]), testQueues, "RandomQueue(containerclass=LinkedList)")
    profiler(map(int,sys.argv[1:]), testPriorityQueues, "*priorityQueueClasses")

