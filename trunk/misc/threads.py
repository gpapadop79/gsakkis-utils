import time, threading
from twisted.internet import reactor
from twisted.python import threadable
threadable.init()

class Safe:
    def __init__(self, x=0):
        self.__x = x
        #super(Safe,self).__init__()
        #self.setDaemon(True)
        self._lock = threading.Lock()

    def incr(self):
        #self._lock.acquire()
        self.__x += 1
        new = self.__x
        time.sleep(.5)
        print new, self.__x
        #self._lock.release()

    def decr(self):
        self._lock.acquire()
        self.__x -= 1
        new = self.__x
        time.sleep(.5)
        print new, self.__x
        self._lock.release()

    def process(self):
        self._lock.acquire()
        x = self.__x
        time.sleep(.5)
        print x, self.__x
        self._lock.release()

    #def __call__(self, x):
    #    # run method in thread
    #    reactor.callInThread(self.aSillyBlockingMethod, x)
    #    #self.aSillyBlockingMethod(x)

foo = Safe()
#foo.start()
#print foo.x
reactor.callLater(2,reactor.stop)
reactor.callInThread(foo.incr);print "hey"
reactor.callInThread(foo.decr);print "hey"
reactor.run()

if 0:
    ts = (threading.Thread(target=foo.incr),
          threading.Thread(target=foo.process),
          threading.Thread(target=foo.decr))
    for t in ts:
        t.start()#; print foo.x
    for t in ts:
        t.join()

#reactor.callLater(3, reactor.stop)
#reactor.run()
#for i in xrange(3):
#    foo.change(1)

