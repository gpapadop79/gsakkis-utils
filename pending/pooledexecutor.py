# todo:
# - activeTasks()
# - thread safe (synchronized methods)
# - callbacks for various events (e.g. exceptions, discarding)
# - testing
# - documentation

import sys, time, threading, Queue

__author__ = "George Sakkis <gsakkis@rutgers.edu>"
__all__ = ["PooledExecutor"]


class PooledExecutor(object):

    def __init__(self, minPoolSize=1, maxPoolSize=None, maxQueueSize=None,
                 keepAliveTime=None):
        assert minPoolSize > 0
        if maxPoolSize is not None:
            assert maxPoolSize >= minPoolSize
        self._poolSize = 0
        self._blockedExecutionHandler = None
        self._maxPoolSize = maxPoolSize
        self._minPoolSize = minPoolSize
        self._taskQueue = self._queueFactory(maxQueueSize)
        self._keepAliveTime = keepAliveTime
        self.runWhenBlocked()

    def execute(self, callable, *args, **kwds):
        while True:
            task = (callable, args, kwds)
            # ensure minimum number of threads
            if self._poolSize < self._minPoolSize:
                self._addThread(task); return
            # Try to give to existing thread without blocking
            try: self._taskQueue.put_nowait(task); return
            except Queue.Full: pass
            # If cannot handoff and still under maximum, create new thread
            maxPoolSize = self._maxPoolSize
            if maxPoolSize is None or self._poolSize < maxPoolSize:
                self._addThread(task); return
            # Cannot hand off and cannot create thread -- ask for help
            if self._blockedExecutionHandler(callable, *args, **kwds):
                return

    def dispatch(self, callables):
        self.waitWhenBlocked()  # don't want to do process in this thread
        productQueue = self._queueFactory()
        expected = 0
        for i,callable in enumerate(callables):
            # needs the "i=i,callable=callable" trick so that these are local
            # instead of being bounded to the last value in the loop
            def wrappedCallable(i=i, callable=callable):
                productQueue.put((i,callable()))
                #return i,callable()
            self.execute(wrappedCallable)
            expected += 1
            # consume what has been consumed so far
            while True:
                try:
                    yield productQueue.get_nowait()
                    expected -= 1
                except Queue.Empty: break
            #print "%d pending.." % expected
        while expected:
            yield productQueue.get()
            #print "%d pending.." % expected
            expected -= 1

    def queuedTasks(self):
        return self._taskQueue.qsize()

    def numThreads(self):
        return self._poolSize

    def runWhenBlocked(self):
        try: handler = self._runWhenBlocked
        except AttributeError:
            def handler(callable, *args, **kwds):
                callable(*args,**kwds); return True
            self._runWhenBlocked = handler
        self._blockedExecutionHandler = handler

    def waitWhenBlocked(self):
        try: handler = self._waitWhenBlocked
        except AttributeError:
            def handler(callable, *args, **kwds):
                self._taskQueue.put((callable,args,kwds))
                return True
            self._waitWhenBlocked = handler
        self._blockedExecutionHandler = handler

    def discardWhenBlocked(self):
        try: handler = self._discardWhenBlocked
        except AttributeError:
            def handler(callable, *args, **kwds):
                #print "!! Task %s discarded !!" % task.id
                return True
            self._discardWhenBlocked = handler
        self._blockedExecutionHandler = handler

    def abortWhenBlocked(self):
        try: handler = self._abortWhenBlocked
        except AttributeError:
            def handler(callable, *args, **kwds):
                raise RuntimeError("Pool is blocked")
            self._abortWhenBlocked = handler
        self._blockedExecutionHandler = handler

    def discardOldestWhenBlocked(self):
        try: handler = self._discardOldestWhenBlocked
        except AttributeError:
            def handler(callable, *args, **kwds):
                old = self._taskQueue.get_nowait()
                #print "!! Task %s replaced task %s!!" % (task.id, old.id)
                try: self._taskQueue.put_nowait((callable,args,kwds))
                except Queue.Full: callable(*args,**kwds)
                return True
            self._discardOldestWhenBlocked = handler
        self._blockedExecutionHandler = handler

    def _queueFactory(self, size=None):
        if size == 0:
            return _DummyQueue()
        if size is None or size < 0:
            return Queue.Queue()
        else:
            return Queue.Queue(size)

    def _addThread(self, task):
        def makeWorker():
            try:
                newTask = task
                if newTask is not None:
                    callable, args, kwds = newTask
                    callable(*args,**kwds)
                    del newTask,callable,args,kwds     # enable GC
                while True:
                    newTask = self._getTask()
                    if newTask is not None:
                        callable, args, kwds = newTask
                        callable(*args,**kwds)
                        del newTask,callable,args,kwds
                    else: break
            finally:
                self._poolSize -= 1
                # Create a replacement if needed
                if self._poolSize < self._minPoolSize:
                    try: self._addThread(self._taskQueue.get_nowait())
                    except Queue.Empty: pass
        self._poolSize += 1
        thread = threading.Thread(target=makeWorker)
        if self._keepAliveTime is None:
            thread.setDaemon(True)
        thread.start()

    def _getTask(self):
        maxPoolSize = self._maxPoolSize
        if maxPoolSize is not None and self._poolSize > maxPoolSize:
            # Cause to die if too many threads
            return None
        keepAliveTime = self._keepAliveTime
        try:
            if keepAliveTime == 0:
                return self._taskQueue.get_nowait()
            else:
                return self._taskQueue.get(timeout=keepAliveTime)
        except Queue.Empty:
            return None


class _DummyQueue(Queue.Queue):
    def qsize(self):
        return 0
    def put(self, item, block=True, timeout=None):
        return self._failOrWait(block,timeout,Queue.Full())
    def get(self, block=True, timeout=None):
        return self._failOrWait(block,timeout,Queue.Empty())
    def _failOrWait(self, block, timeout, exception):
        if block:
            if timeout is not None:
                # sleep for timeout and raise Full exception
                time.sleep(timeout)
            else:
                # wait forever
                while True: time.sleep(3600)
        raise exception
