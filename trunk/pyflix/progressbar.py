'''Provides progress bar capabilities to console programs.

@sort: ProgressBar,IterableProgressBar,FileProgressBar
'''

__all__ = ['ProgressBar', 'IterableProgressBar', 'FileProgressBar', 'progress']
__author__ = 'George Sakkis <george.sakkis AT gmail.com>'

import sys
from array import array

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

    def __init__(self, min, max, width=79, stream=sys.stderr):
        '''        
        @param min,max: The minimum and maximum bounds for the iteration.
        @type min,max: Number (int or float)
        '''
        if min >= max:
            raise ValueError('min value should be lower than max')
        self._bar = array('c', '[]')
        self.out = stream
        self._width = width - len(self._bar)
        self._min,self._max = map(float, (min,max))
        self._span = self._max - self._min
        for _ in xrange(self._width):
            self._bar.insert(1,' ')
        self.reset()

    def reset(self):
        '''To be called before reusing this ProgressBar.'''
        self._amount = self._min
        self._numHashes = self._roundedPercentDone = 0
        for i in xrange(1,self._width+1):
            self._bar[i] = ' '
        del self._bar[self._width+2:]

    def update_to(self, amount):
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
            print >> self.out, self._bar.tostring(), '\r',
            self.out.flush()

    def update_by(self, amount=1):
        '''Inform this progress bar about the progress of the displayed procedure.

        @param amount: A number that indicates how much has the procedure
            advanced since the previous call (or the beginning if this is the
            first call).
        '''
        self.update_to(self._amount+amount)

    def irange(self, step=1, refresh=None, relative=False):
        '''Iterate over the range(min,max,step) updating this progress bar every
        C{refresh}.
        
        @param step: The step of the iteration.
        @type step: Number (int or float)
        @param refresh: Determines how often should the progress bar reflect
            the progress of the procedure. Typically a multiple of C{step}, or
            None for equal to C{step}.
        @param relative: True if C{refresh} denotes a fraction of the whole
            procedure (e.g. 1%) or False for absolute refresh.
        '''
        self.reset()
        if refresh is None:
            refresh = step
        elif relative:
            if not (0 < refresh < 1):
                raise ValueError('Relative refresh must be a percentage')
            refresh *= self._max-self._min
        current = self._min; last_updated = -1
        while (current-self._max)*step < 0:
            # XXX: don't use 'amount % refresh == 0' because refresh maybe float < 1
            div = current // refresh
            if div != last_updated:
                self.update_to(current)                 
                last_updated = div
            yield current
            current += step
        # update one final time after completion
        self.update_to(current)
        print >> self.out
    
#====== IterableProgressBar ====================================================

class IterableProgressBar(ProgressBar):
    '''A L{ProgressBar} that wraps an iterable.'''

    def __init__(self, iterable, size=None, width=79, stream=sys.stderr):
        '''
        @param size: The length of the iterable. If None, then the size is
            determined by attempting to call C{len}, or if this fails, by
            iterating over the iterable.
        '''
        self._iterable = iterable
        if size is None:
            size = len(iterable)
        ProgressBar.__init__(self, 0, size, width, stream)

    def __iter__(self):
        return self.progress()

    def progress(self, refresh=1):
        next = iter(self._iterable).next
        for _ in self.irange(1, refresh, relative=refresh<1):
            yield next()

#====== FileProgressBar ========================================================

class FileProgressBar(IterableProgressBar):
    '''An L{IterableProgressBar} that wraps a file.'''

    def __init__(self, path, width=79, stream=sys.stderr):
        '''
        @param path: The path of the file to be monitored.
        '''
        self._path = path
        size = sum(1 for line in open(path))
        IterableProgressBar.__init__(self, open(path), size, width, stream)

    def reset(self):
        IterableProgressBar.reset(self)
        self._iterable = open(self._path)

#====== iterprogress ===========================================================

def progress(iterable, size=None, refresh=1, width=79, stream=sys.stderr):
    return IterableProgressBar(iterable,size,width,stream).progress(refresh)

if __name__ == '__main__':
    import time
    x = []
    for i in progress('abcdefg'*2, width=70, refresh=1):
        time.sleep(.1)
        x.append(i)
    print x
