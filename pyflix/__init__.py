import sys
from time import time

def timeCall(msg, func, *args, **kwds):
    start = time()
    r = func(*args,**kwds)
    m,s = divmod(time()-start,60)
    print >> sys.stderr, '%s in %d minutes and %.2f seconds' % (msg,m,s)
    return r


