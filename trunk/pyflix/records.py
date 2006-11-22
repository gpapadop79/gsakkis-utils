__all__ = ['Record', 'RatedRecord', 'UnratedRecord',
           'UnratedMovieRecord', 'UnratedUserRecord',
           'RatedMovieRecord', 'RatedUserRecord']

import mmap
from struct import pack
from itertools import izip
import numpy as N
from path import path

from progressbar import ProgressBar

#====== types pertinent to the binary files sorted by movie and by user ========

MOVIE_ID_TYPECODE = 'H' # unsigned short
USER_ID_TYPECODE  = 'L' # unsigned long

class _MovieTypes(object):
    _KeyDtype   = MOVIE_ID_TYPECODE       
    _ValueDtype = USER_ID_TYPECODE    
    # XXX: N.repeat requires the second arg to be convertible to int32
    _CountDtype = 'l'       # number of users that rated a single movie
    
class _UserTypes(object):        
    _KeyDtype   = USER_ID_TYPECODE
    _ValueDtype = MOVIE_ID_TYPECODE
    _CountDtype = 'H'      # number of movies rated by a single user


#====== Base abstract record type ==============================================

class Record(object):
    __slots__ = ('id', '_values')

    def __init__(self, key, values, counts):
        raise NotImplementedError('Abstract class')

    @classmethod
    def fromfile(cls, datfile, readbuffer=128*1024**2, progressbar=False):
        from struct import unpack
        size = path(datfile).size
        f = open(datfile,'rb+',readbuffer)
        m = mmap.mmap(f.fileno(), size, 
                      access=mmap.ACCESS_READ)
        kdtype, cdtype, vdtype = cls._KeyDtype, cls._CountDtype, cls._ValueDtype
        ksize, csize, vsize = [N.dtype(t).itemsize for t in kdtype,cdtype,vdtype]
        num_partitions = cls._num_partitions()
        csize *= num_partitions
        if progressbar:
            if not isinstance(progressbar, ProgressBar):
                progressbar = ProgressBar(0, size, width=70)
        read = m.read
        for key in iter(lambda:read(ksize), ''):
            # 1. unpack the key
            key = unpack(kdtype,key)[0]
            # 2. read the partition counts
            counts = N.fromstring(read(csize), cdtype, num_partitions)
            # 3. read the values
            num_values = N.sum(counts)
            values = N.fromstring(read(vsize*num_values), vdtype, num_values)
            if progressbar:
                progressbar.update_to(m.tell())
            yield cls(key, values, counts)
        print >> progressbar.out

    @classmethod
    def fromvalues(cls, key, partitioned_values):
        counts = map(len,partitioned_values)
        values = []
        for v in partitioned_values:
            v.sort() # sort the values in each partition
            values.extend(v)
        return cls(key, values, counts)

    def values(self):        
        raise NotImplementedError
                    
    @staticmethod
    def commonValues(*records):
        '''Return the common values of the given records.'''
        return intersect_arrays(*[record.values() for record in records])

    @classmethod
    def _num_partitions(cls):
        raise NotImplementedError

#====== Unrated record types ===================================================

class UnratedRecord(Record):
    '''A simple record type composed of a key (id) and an array of values.'''
    
    def __init__(self, key, values, counts=None):
        self.id = key
        self._values = N.array(values, self._ValueDtype)
    
    def values(self):        
        return self._values
                            
    def tostring(self):
        return ''.join([pack(self._KeyDtype, self.id),
                        pack(self._CountDtype, len(self._values)),
                        self._values.tostring()])
        
    def __str__(self):
        return str((self.id, self._values))

    @classmethod
    def _num_partitions(cls):
        return 1

class UnratedMovieRecord(UnratedRecord, _MovieTypes):
    pass

class UnratedUserRecord(UnratedRecord, _UserTypes):
    pass


#====== Rated record types =====================================================

class RatedRecord(Record):

    __slots__ = Record.__slots__ + ('_counts',)
        
    def __init__(self, key, values, counts):
        self.id = key
        self._values = N.array(values, self._ValueDtype)
        self._counts = N.array(counts, self._CountDtype)
    
    #--------- accessors -------------------------------------------------------
                    
    def values(self, min_rating=None, max_rating=None):        
        if min_rating is max_rating is None: # optimize default case
            return self._values
        value_indices = N.add.accumulate(self._counts)
        s = self._normalizeSlice(min_rating,max_rating)
        if s.start > 0:
            start = value_indices[s.start-1]
        else:
            start = 0
        return self._values[start:value_indices[s.stop-1]]
            
    def ratings(self, min_rating=None, max_rating=None):
        if min_rating is max_rating is None: # optimize default case
            return N.repeat(self._AllRatings, self._counts)
        s = self._normalizeSlice(min_rating,max_rating)
        return N.repeat(self._AllRatings[s], self._counts[s])

    def iterValueRatings(self, min_rating=None, max_rating=None):        
        if min_rating is max_rating is None: # optimize default case
            return izip(self._values, N.repeat(self._AllRatings,self._counts))
        return izip(self.values(min_rating,max_rating),
                    self.ratings(min_rating,max_rating))
    
    #--------- joining records -------------------------------------------------
    
    @staticmethod
    def commonValues(*records, **min_max_ratings):
        '''Return the common values of the given records.
        
        @param min_max_ratings: Optional 'min_rating' and 'max_rating' arguments
        '''
        args = [min_max_ratings.get(name) for name in 'min_rating','max_rating']
        return intersect_arrays(*[record.values(*args) for record in records])
    
    @staticmethod
    def jointRatings(*records, **min_max_ratings):
        '''Return a 2-D array whose A[i,j] element is the rating of records[i]
        for the j-th common value returned by C{common_values()}.
        '''
        return RatedRecord._jointValueRatings(*records, **min_max_ratings)[1]
    
    @staticmethod
    def iterCommonValuesRatings(*records, **min_max_ratings):
        '''Iterate over (common_value,ratings) tuples for each common_value 
        returned by C{common_values()}, where ratings is the array of ratings
        given for this common_value by all records.
        '''
        common_values, joint_ratings = RatedRecord._jointValueRatings(*records,
                                                                  **min_max_ratings)
        for i,value in enumerate(common_values):
            yield (value, joint_ratings[:,i])
    
    #--------- string representation -------------------------------------------
    
    def tostring(self):
        return ''.join([pack(self._KeyDtype, self.id),
                        self._counts.tostring(), self._values.tostring()])
        
    def __str__(self):
        return str((self.id, self._counts, self._values))
        
    #--------- internal attributes ---------------------------------------------

    _AllRatings = N.arange(1,6,dtype=N.uint8)

    @classmethod
    def _num_partitions(cls):
        return len(cls._AllRatings)
        
    def _normalizeSlice(self, min_rating, max_rating):
        get_index = lambda x: N.where(self._AllRatings==x)[0][0]
        if min_rating is not None:
            min_rating = get_index(min_rating)
        else:
            min_rating = 0
        if max_rating is not None:
            max_rating = get_index(max_rating) + 1
        else:
            max_rating = len(self._AllRatings)
        return slice(min_rating,max_rating)

    @staticmethod
    def _jointValueRatings(*records, **min_max_ratings):
        args = [min_max_ratings.get(name) for name in 'min_rating','max_rating']
        values_list = [record.values(*args) for record in records]
        common_values = intersect_arrays(*values_list)
        joint_ratings = N.empty((len(records),len(common_values)),
                                dtype=RatedRecord._AllRatings.dtype)
        if len(common_values):
            for i,values in enumerate(values_list):
                # sort the values because N.searchsorted requires it
                s_indices = values.argsort()
                # find the indices of the common values
                c_indices = N.searchsorted(values[s_indices], common_values)
                # take the ratings for the i-th record and rearrange them according to s_indices 
                ratings = records[i].ratings(*args)[s_indices]
                # and finally take the corresponding ratings for the common values
                joint_ratings[i] = ratings[c_indices]
        return (common_values, joint_ratings)


class RatedMovieRecord(RatedRecord, _MovieTypes):
    pass

class RatedUserRecord(RatedRecord, _UserTypes):
    pass


#===============================================================================

def intersect_arrays(*arrays):
    '''Intersection of 1D arrays with unique elements.'''
    current = arrays[0]
    for i in xrange(1,len(arrays)):
        aux = N.concatenate((current,arrays[i]))
        aux.sort()
        current = aux[aux[1:] == aux[:-1]]
    return current
