# implemented in core as slice.indices

def sliceIndices(slice, length):
    '''Return the slice's (start,stop,step) indexes.

    Return a tuple (start,stop,step) so that range(start,stop,step) is the
    list of indexes for the given C{slice} in a sequence of length C{length}.

    Preconditions::
        - isinstance(length,int) and length >= 0
        - slice.start is None or isinstance(slice.start,int)
        - slice.stop is None or isinstance(slice.stop,int)
        - slice.step is None or isinstance(slice.step,int)
        - slice.step != 0

    Postconditions::
        - isinstance(step,int) and step != 0
        - isinstance(start,int) and -1 < start < length
        - isinstance(stop,int) and -1 <= stop <= length

    Examples:
        For a list of length 5::
            TODO
    '''
    if not isinstance(length,int) or length < 0:
        raise TypeError("length should be non-negative")
    start,stop,step = slice.start,slice.stop,slice.step
    for val in start,stop,step:
        if not (val is None or isinstance(val,int)):
            raise TypeError("slice indices must be integer")
    # normalize step
    if step is None:
        step = 1
    elif step == 0:
        raise TypeError("slice step cannot be zero")
    # normalize stop
    if stop is None:
        if step>0: stop = length
        else: stop = -1
    elif stop>length:
        stop = length
    elif stop<0:
        stop += length
        if stop<0: stop = -1
    # normalize start
    if start is None:
        if step>0: start = 0
        else: start = length-1
    elif start>=length:
        if step<0:
            start = length-1
        else:
            start = length
    elif start<0:
        start += length
        if start<0:
            if step>0:
                start = max(start,0)
            else:
                start = -1
    assert isinstance(step,int) and step != 0
    assert isinstance(start,int) and -1 <= start <= length
    assert isinstance(stop,int) and -1 <= stop <= length
    return start,stop,step


import unittest

class NormalizeSliceTestCase(unittest.TestCase):
    class Sequence:
        def __init__(self,s):
            self._sequence = s

        def __getitem__(self, indexOrSlice):
            s = self._sequence
            if not isinstance(indexOrSlice,slice):
                return s[indexOrSlice]
            return type(s)(map(s.__getitem__,
                               range(*normalizeSlice(indexOrSlice, len(s)))))

    def testSlicing(self):
        s = self.Sequence(aSequence)
        for slice in iterSlices(aSequence,nonZeroStep=False):
            if slice.step != 0:
                self.assertEquals(aSequence[slice], s[slice])
            else:
                self.assertRaises(TypeError, s.__getitem__, slice)


