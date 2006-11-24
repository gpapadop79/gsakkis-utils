__all__ = ['AbstractDataset', 'UnratedDataset', 'RatedDataset', 'writePredictions']

#==== imports ==================================================================

import mmap
import cPickle
import numpy as N
from path import path

from pyflix.records import *
from pyflix.setup import iterQset
from pyflix.progressbar import ProgressBar

#==== Abstract dataset =========================================================

class AbstractDataset(object):

    def __init__(self, dir):
        dir = path(dir)
        self._movies = self._users = None
        if (dir/'movies.idx').exists() and (dir/'movies.dat').exists():
            self._movies = Index(dir/'movies.idx', dir/'movies.dat', self._MovieRecordType)
        if (dir/'users.idx').exists() and (dir/'users.dat').exists():
            self._users = Index(dir/'users.idx', dir/'users.dat', self._UserRecordType)

    def iterMoviesUsers(self):
        '''Return an iterator over all (movie,user) pairs of this dataset.'''
        if self._movies is not None:
            for movie_id, movie in self._movies.iteritems():
                for user_id in movie.values():
                    yield (movie_id, user_id)
        else:
            for user_id, user in self._users.iteritems():
                for movie_id in user.values():
                    yield (movie_id, user_id)
            
    def movies(self, *users):
        '''Return an array of the movie IDs rated by the given user(s).
        
        If no users are given, return all the movie IDs of this dataset.
        Otherwise, return the IDs of the movies that have been rated by ALL the
        given users.
        '''
        if users:
            return AbstractRecord.commonValues(self._users[u] for u in users)
        else:
            return N.array(self._movies.keys(), dtype=MOVIE_ID_TYPECODE)
    
    def users(self, *movies):
        '''Return an array of the user IDs that rated the given movie(s).
        
        If no movies are given, return all the user IDs of this dataset.
        Otherwise, return the IDs of the users that have rated ALL the given movies.
        '''
        if movies:
            return AbstractRecord.commonValues(self._movies[m] for m in movies)
        else:
            return N.array(self._users.keys(), dtype=USER_ID_TYPECODE)
        
    _MovieRecordType = NotImplemented
    _UserRecordType = NotImplemented

#==== Unrated dataset ==========================================================

class UnratedDataset(AbstractDataset):
    _MovieRecordType = UnratedMovieRecord
    _UserRecordType = UnratedUserRecord

#==== Rated dataset ==========================================================

class RatedDataset(AbstractDataset):

    def iterMoviesUsersRatings(self, min_rating=None, max_rating=None,
                               progressbar=False):
        '''Return an iterator over all (movie,user,rating) tuples of this dataset.'''
        if self._movies is not None:
            if progressbar:
                progressbar = ProgressBar(0, len(self._movies), width=70)
            for movie_id,movie in self._movies.iteritems():
                if progressbar: progressbar.update() 
                for user_id, rating in movie.iterValueRatings(min_rating,max_rating):
                    yield (movie_id, user_id, rating)
        else:
            if progressbar:
                progressbar = ProgressBar(0, len(self._users), width=70)
            for user_id,user in self._users.iteritems():
                if progressbar: progressbar.update()
                for movie_id, rating in user.iterValueRatings(min_rating,max_rating):
                    yield (movie_id, user_id, rating)
        if progressbar:
            print >> progressbar.out

    def movies(self, *users, **min_max_ratings):
        '''Return an array of the movie IDs rated by the given user(s).
        
        If no users are given, return all the movie IDs of this dataset.
        Otherwise, return the IDs of the movies that have been rated by ALL the
        given users.
        '''
        if users:
            return RatedRecord.commonValues((self._users[u] for u in users),
                                            **min_max_ratings)
        else: return AbstractDataset.movies(self)

    def users(self, *movies, **min_max_ratings):
        '''Return an array of the user IDs that rated the given movie(s).
        
        If no movies are given, return all the user IDs of this dataset.
        Otherwise, return the IDs of the users that have rated ALL the given movies.
        '''
        if movies:
            return RatedRecord.commonValues((self._movies[m] for m in movies),
                                            **min_max_ratings)
        else: return AbstractDataset.users(self)

    def rmse(self, algorithm, progressbar=False):
        s,n = 0.0,0
        for movie,user,rating in self.iterMoviesUsersRatings(progressbar=progressbar):
            d = algorithm(movie,user) - rating
            s += d*d
            n += 1
        return (s/n) ** 0.5

    #---- ratings accessors and iterators for a single movie or user -----------
    
    def ratingsTo(self, movie, min_rating=None, max_rating=None):
        '''Return an array of the given movie's ratings.'''
        return self._movies[movie].ratings(min_rating,max_rating)

    def ratingsBy(self, user, min_rating=None, max_rating=None):
        '''Return an array of the given user's ratings.'''
        return self._users[user].ratings(min_rating,max_rating)
    
    def iterUsersRatings(self, movie, min_rating=None, max_rating=None):
        '''Return an iterator over all (user,rating) pairs for the given movie.'''
        return self._movies[movie].iterValueRatings(min_rating,max_rating)
        
    def iterMoviesRatings(self, user, min_rating=None, max_rating=None):
        '''Return an iterator over all (movie,rating) pairs for the given user.'''
        return self._users[user].iterValueRatings(min_rating,max_rating)
    
    #---- ratings accesors and iterators for jointly rated movies and users ----
    
    def ratingsMatrixTo(self, *movies, **min_max_ratings):
        '''Return the ratings of the users that rated ALL the given movies.
        
        Return a 2-D array whose [i,j] element is the rating of the j-th movie
        by the i-th user returned from self.users(*movies).
        '''
        return RatedRecord.jointRatings((self._movies[m] for m in movies),
                                        **min_max_ratings)

    def ratingsMatrixBy(self, *users, **min_max_ratings):
        '''Return the ratings of the movies that were rated by ALL the given users.
        
        Return a 2-D array whose [i,j] element is the rating of the j-th user
        to the i-th movie returned from self.movies(*users).
        '''
        return RatedRecord.jointRatings((self._users[u] for u in users),
                                        **min_max_ratings)
            
    def iterJointUsersRatings(self, *movies, **min_max_ratings):
        '''Return an iterator over (user,ratings) pairs for each user that rated
        ALL the given movies. 'ratings' is a len(movies) 1-D array.
        '''
        return RatedRecord.iterCommonValuesRatings(
            (self._movies[m] for m in movies), **min_max_ratings)
    
    def iterJointMoviesRatings(self, *users, **min_max_ratings):
        '''Return an iterator over (movie,ratings) pairs for each movie rated by
        ALL the given users. 'ratings' is a len(users) 1-D array.
        '''
        return RatedRecord.iterCommonValuesRatings(
            (self._users[u] for u in users), **min_max_ratings)
        
    _MovieRecordType = RatedMovieRecord
    _UserRecordType = RatedUserRecord

#==== writePredictions =========================================================

def writePredictions(qualifying_txt, output, algorithm, format='%.3f'):
    if not hasattr(output, 'read'):
        output = open(output, 'w')
    last_movie_id = None
    for movie_id,user_id in iterQset(qualifying_txt):
        if movie_id != last_movie_id:
            print >> output, '%d:' % movie_id
            last_movie_id = movie_id
        print >> output, format % algorithm(movie_id,user_id)

#==== Data index ===============================================================

class Index(object):
    def __init__(self, indexpath, datpath, recordtype):
        # load the index file
        self._key2index = cPickle.load(open(indexpath,'rb'))
        # open the data file and mmap it
        f = open(datpath, 'rb+')
        self._datfile = datfile = mmap.mmap(f.fileno(), path(f.name).size,
                                            access=mmap.ACCESS_READ)
        fromfile = recordtype.fromfile
        self._readrecord = lambda: fromfile(datfile)
        
    def __getitem__(self, key):
        self._datfile.seek(self._key2index[key])
        return self._readrecord()
    
    def __len__(self):
        return len(self._key2index)
    
    def iterkeys(self):
        return self._key2index.iterkeys()

    def itervalues(self):
        self._datfile.seek(0)
        # iterate over all the records one after the other; no need to seek() 
        for _ in xrange(len(self._key2index)):
            yield self._readrecord()
    
    def iteritems(self):
        self._datfile.seek(0)
        for key in self._key2index:
            yield key,self._readrecord()
    
    __iter__ = iterkeys

    def keys(self): return list(self.iterkeys())
    def values(self): return list(self.itervalues())
    def items(self): return list(self.iteritems())
        
    
if __name__ == '__main__':
    import sys
    d = RatedDataset(sys.argv[1])
    
    if 0:
        algorithm = lambda m,u: 3.6
        print d.rmse(algorithm)
        ##writePredictions(sys.argv[1], 'dummy.txt', algorithm)
    from pyflix import timeCall
    
    #print timeCall('d.users(6)', d.users, 6)
    q = UnratedDataset(sys.argv[1])
    print q.movies()
    
    print timeCall('d.movies(6)', d.movies, 6)
    
    for m,u,r in d.iterMoviesUsersRatings():
        print m,u,r
