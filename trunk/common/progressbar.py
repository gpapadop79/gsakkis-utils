'''Provides progress bar capabilities to console programs.

@sort: ProgressBar,IterableProgressBar,FileProgressBar
'''

import sys
from array import array

__author__ = 'George Sakkis <gsakkis@rutgers.edu>'
__all__ = ['ProgressBar', 'IterableProgressBar', 'FileProgressBar']


#====== ProgressBar ===========================================================

class ProgressBar(object):
    '''Basic progress bar class.

    Allows a client to display the progress of a procedure in the form of a
    progress bar as well as the actual percentage done, rounded to an integer::
        [*************                                ] 33%

    The client L{initializes <__init__>} a ProgressBar by specifying a minimum
    (usually 0) and a maximum (e.g. number of procedure steps, file size,
    etc.) number, and optionally the width of the progress bar and the output
    stream to display it (standard error by default).
    '''

    def __init__(self, min, max, width=79, outstream=sys.stderr):
        self._bar = array('c', '[]')
        self._out = outstream
        self._width = width - len(self._bar)
        self._min,self._max = map(float, (min,max))
        self._span = self._max - self._min
        for i in xrange(self._width):
            self._bar.insert(1,' ')
        self.reset()

    def reset(self):
        '''To be called before reusing this ProgressBar.

        Call this to to reset the ProgressBar if L{update} or L{run} has been
        called at least once.
        '''
        self._amount = self._min
        self._numHashes = self._roundedPercentDone = 0
        for i in xrange(1,self._width+1):
            self._bar[i] = ' '
        del self._bar[self._width+2:]

    def update(self, amount):
        '''Inform this progress bar about the progress of the displayed procedure.

        @param amount: A number between the min and max specified in L{__init__}.
        '''
        self._amount = amount
        percentDone = (amount-self._min) / self._span
        new_roundedPercentDone = int(round(percentDone*100))
        new_numHashes = int(round(percentDone*self._width))
        changed = False
        if self._numHashes < new_numHashes:
            for i in xrange(self._numHashes, new_numHashes):
                self._bar[i+1] = '*'
            self._numHashes = new_numHashes
            changed = True
        if self._roundedPercentDone < new_roundedPercentDone:
            self._roundedPercentDone = new_roundedPercentDone
            percentString = array('c', ' %d%%' % new_roundedPercentDone)
            startIndex = self._width+2
            self._bar[startIndex:startIndex+len(percentString)] = percentString
            changed = True
        if changed:
            print >> self._out, self._bar.tostring(), '\r',
            self._out.flush()

    def incrementBy(self, amount=1):
        '''Inform this progress bar about the progress of the displayed procedure.

        @param amount: A number that indicates how much has the procedure
            advanced since the previous call (or the beginning if this is the
            first call).
        '''
        self.update(self._amount+amount)

    def run(self, callable, step=1, update_step=None):
        '''Invoke repeatedly a callable and keep displaying its progress.

        @param callable: A callable f(amount) to be called repeatedly for all
            amounts from min up to (but not including) max with the given C{step}.
        @param step: The value by which the amount passed to C{callable} is
            incremented (or decremented if it is negative).
        @param update_step: Determines how often should the progress bar
            reflect the progress of the procedure. Typically a multiple of
            C{step}, or None for equal to C{step}.
        '''
        self.reset()
        if update_step is None:
            update_step = step
        amount = self._min
        while (amount - self._max)*step < 0:
            # XXX: don't use 'amount % update_step == 0' because update_step
            # maybe float < 1
            div = amount/update_step
            if div == int(div):
                self.update(amount)
            callable(amount)
            amount += step
        # update one final time after completion
        self.update(amount)
        print


#====== IterableProgressBar ==================================================

class IterableProgressBar(ProgressBar):
    '''A L{ProgressBar} that wraps an iterable.'''

    def __init__(self, iterable, size=None, **kwds):
        '''
        @param size: The length of the iterable. If None, then the size is
            determined by attempting to call C{len}, or if this fails, by
            iterating over the iterable.
        '''
        self._iterable = iterable
        if size is None:
            size = length(iterable)
        super(IterableProgressBar,self).__init__(0, size, **kwds)

    def runforall(self, callable, update_step=1):
        '''Invoke repeatedly a callable for every item of the iterable and
        keep displaying its progress.

        @param callable: A callable f(item) to be called repeatedly for every
            item returned by the iterable specified in the L{__init__}.
        @param update_step: Determines how often should the progress bar
            reflect the progress of the procedure.
        '''
        self.reset()
        i=-1
        for i,item in enumerate(self._iterable):
            if i%update_step == 0:
                self.update(i)
            callable(item)
        # update one final time after completion
        self.update(i+1)
        print


#====== FileProgressBar ======================================================

class FileProgressBar(IterableProgressBar):
    '''An L{IterableProgressBar} that wraps a file.

    Essentially L{runforall} expects a callable C{f(line)} to be invoked for
    every line of the file.
    '''

    def __init__(self, path, **kwds):
        '''
        @param path: The path of the file to be monitored.
        '''
        super(FileProgressBar,self).__init__(open(path), **kwds)
        self._path = path

    def reset(self):
        super(FileProgressBar,self).reset()
        self._iterable = open(self._path)


#====== module helpers =======================================================

def length(iterable):
    try: return len(iterable)
    except:
        count = 0
        for i in iterable: count += 1
        return count


if __name__ == '__main__':
    import time
    bar = IterableProgressBar(xrange(0,50))
    bar.run(lambda i: time.sleep(.2), step=2)
    bar.runforall(lambda x: time.sleep(.2))
