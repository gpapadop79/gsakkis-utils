__all__ = ['AbstractRecord', 'RatedRecord', 'UnratedRecord',
           'UnratedMovieRecord', 'UnratedUserRecord',
           'RatedMovieRecord', 'RatedUserRecord',
           'MOVIE_ID_TYPECODE', 'USER_ID_TYPECODE']

#==== imports ==================================================================

from struct import pack,unpack
from itertools import izip,imap,chain
import numpy as N

#====== types pertinent to the movie and user binary files =====================

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

def itemsize(dtype):
    try: memo = itemsize._memo
    except AttributeError: memo = itemsize._memo = {}
    try: return memo[dtype]
    except KeyError:
        d = memo[dtype] = N.dtype(dtype).itemsize
        return d        

#====== Base abstract record type ==============================================

class AbstractRecord(object):
    __slots__ = ('id', '_values')

    def values(self):        
        raise NotImplementedError

    @classmethod
    def fromfile(cls, datfile):
        '''Read the record that starts at the current position of the given file.
        
        @param datfile: A file-like object.
        '''
        read = datfile.read
        num_counts = cls._num_counts
        kdtype, cdtype, vdtype = cls._KeyDtype, cls._CountDtype, cls._ValueDtype
        # 1. read the key
        key = unpack(kdtype,read(itemsize(kdtype)))[0]
        # 2. read the partition counts
        counts = N.fromstring(read(num_counts*itemsize(cdtype)), cdtype, num_counts)
        # 3. read the values
        num_values = counts.sum()
        values = N.fromstring(read(num_values*itemsize(vdtype)), vdtype, num_values)
        return cls(key, values, counts)

    @classmethod
    def fromvalues(cls, key, partitioned_values):
        counts = N.fromiter(imap(len,partitioned_values), cls._CountDtype)        
        values = N.fromiter(chain(*(imap(sorted,partitioned_values))), cls._ValueDtype)
        return cls(key, values, counts)
                    
    @staticmethod
    def commonValues(records):
        '''Return the common values of the given records.'''
        return intersect_arrays(record.values() for record in records)

    _num_counts = NotImplemented

#====== Unrated record types ===================================================

class UnratedRecord(AbstractRecord):
    '''A simple record type composed of a key (id) and an array of values.'''
    
    def __init__(self, key, values, counts=None):
        assert values.dtype == self._ValueDtype
        self.id = key
        self._values = values
    
    def values(self):        
        return self._values
                            
    def tostring(self):
        return ''.join([pack(self._KeyDtype, self.id),
                        pack(self._CountDtype, len(self._values)),
                        self._values.tostring()])
        
    def __str__(self):
        return str((self.id, self._values))

    _num_counts = 1


class UnratedMovieRecord(UnratedRecord, _MovieTypes):
    pass

class UnratedUserRecord(UnratedRecord, _UserTypes):
    pass

#====== Rated record types =====================================================

class RatedRecord(AbstractRecord):

    __slots__ = AbstractRecord.__slots__ + ('_counts',)
        
    def __init__(self, key, values, counts):
        assert values.dtype == self._ValueDtype and counts.dtype == self._CountDtype
        self.id = key
        self._values = values 
        self._counts = counts
    
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
    def commonValues(records, min_rating=None, max_rating=None):
        '''Return the common values of the given records.'''
        return intersect_arrays(record.values(min_rating,max_rating)
                                for record in records)
    
    @staticmethod
    def jointRatings(records, min_rating=None, max_rating=None):
        '''Return a 2-D array whose A[i,j] element is the rating of records[i]
        for the j-th common value returned by C{common_values()}.
        '''
        return RatedRecord._jointValueRatings(records, min_rating,max_rating)[1]
    
    @staticmethod
    def iterCommonValuesRatings(records, min_rating=None, max_rating=None):
        '''Iterate over (common_value,ratings) tuples for each common_value 
        returned by C{common_values()}, where ratings is the array of ratings
        given for this common_value by all records.
        '''        
        return izip(*RatedRecord._jointValueRatings(records, min_rating, max_rating))
    
    #--------- string representation -------------------------------------------
    
    def tostring(self):
        return ''.join([pack(self._KeyDtype, self.id), self._counts.tostring(),
                                                       self._values.tostring()])
        
    def __str__(self):
        return str((self.id, self._counts, self._values))
        
    #--------- internal attributes ---------------------------------------------

    _AllRatings = N.arange(1,6,dtype=N.uint8)
    _num_counts = len(_AllRatings)
        
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
    def _jointValueRatings(records, min_rating=None, max_rating=None):
        if not (hasattr(records, '__getitem__') and hasattr(records,'__len__')):
            records = list(records)        
        values_list = [record.values(min_rating,max_rating) for record in records]
        common_values = intersect_arrays(values_list)
        joint_ratings = N.empty((len(common_values),len(records)),
                                dtype=RatedRecord._AllRatings.dtype)
        if len(common_values):
            for i,values in enumerate(values_list):
                # sort the values because N.searchsorted requires it
                s_indices = values.argsort()
                # find the indices of the common values
                c_indices = N.searchsorted(values[s_indices], common_values)
                # take the ratings for the i-th record and rearrange them according to s_indices 
                ratings = records[i].ratings(min_rating,max_rating)[s_indices]
                # and finally assign to the i-th column the corresponding ratings
                # for the common values
                joint_ratings[:,i] = ratings[c_indices]
        return (common_values, joint_ratings)


class RatedMovieRecord(RatedRecord, _MovieTypes):
    pass

class RatedUserRecord(RatedRecord, _UserTypes):
    pass

#===============================================================================

def intersect_arrays(arrays):
    '''Intersection of 1D arrays with unique elements.'''
    arrays = iter(arrays)
    current = arrays.next()
    for array in arrays:
        aux = N.concatenate((current,array))
        aux.sort()
        current = aux[aux[1:] == aux[:-1]]
    return current
