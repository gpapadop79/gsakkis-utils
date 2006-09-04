from poolexecutor import PooledExecutor

if __name__ == '__main__':
    import time,random
    class Task:
        def __init__(self, id):
            self.id = id

        def __call__(self, x):
            id = self.id
            threadname = threading.currentThread().getName()
            print "* [%s] Started task id %s !" % (threadname,id)
            for i in xrange(0,101,20):
                time.sleep(random.random())
                print "[%s] Task id: %s, percent complete: %d (args: %s)" % (
                    threadname, id, i, x)
            print "* [%s] Finished task id %s !" % (threadname,id)

    minPoolSize,maxPoolSize,numWorkers,requests = map(int,sys.argv[1:])
    minPoolSize = max(1,minPoolSize)
    if maxPoolSize < 1: maxPoolSize = None
    pool = PooledExecutor(minPoolSize,maxPoolSize,numWorkers)
    pool.discardWhenBlocked() #waitWhenBlocked() #abortWhenBlocked()
    if 0:
        for i in xrange(requests):
            try: pool.execute(Task(i), i**2)
            except RuntimeError, why: print why
    import math
    def sqrt(x):
        time.sleep(random.random())
        return math.sqrt(x)
    from itertools import count
    tasks = (lambda x=n: sqrt(x) for n in count())
    if 1:
        now = time.time()
        #ll = list(lambda x=n: sqrt(x) for n in xrange(100,145))
        #for l in ll: print l()
        for i,(n,s) in enumerate(pool.dispatch(tasks)):
            #print time.time()-now, n ,s
            print "%d: The sqrt of %d is %s" % (i,n,s)
            #if n>30: break
    else:
        print sorted(pool.dispatch(tasks))
