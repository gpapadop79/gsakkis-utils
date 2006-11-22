#!/usr/bin/env python

__all__ = ['Dataset', 'RatedDataset']

import numpy as N
from path import path

from records import *
from records import MOVIE_ID_TYPECODE, USER_ID_TYPECODE


class Dataset(object):

    def __init__(self, dir):
        dir = path(dir)
        # XXX: allocate an extra dummy movie at index 0 making the list effectively 1-based
        self._movies = [None]
        self._movies.extend(self._MovieRecordType.fromfile(dir/'movies.dat'))
        self._users = users = {}
        for user in self._UserRectordType.fromfile(dir/'users.dat'):
            users[user.id] = user

    def iterMoviesUsers(self):
        '''Return an iterator over all (movie,user) pairs of this dataset.'''
        enum_movies = enumerate(self._movies)
        enum_movies.next() # ignore the dummy movie
        for movie_id, movie in enum_movies:
            for user_id in movie.values():
                yield (movie_id, user_id)

    def movies(self, *users):
        '''Return an array of the movie IDs rated by the given user(s).
        
        If no users are given, return all the movie IDs of this dataset.
        Otherwise, return the IDs of the movies that have been rated by ALL the
        given users.
        '''
        if users:
            return Record.commonValues(*[self._users[u] for u in users])
        else:
            return N.arange(1, len(self._movies), dtype=MOVIE_ID_TYPECODE)
    
    def users(self, *movies):
        '''Return an array of the user IDs that rated the given movie(s).
        
        If no movies are given, return all the user IDs of this dataset.
        Otherwise, return the IDs of the users that have rated ALL the given movies.
        '''
        if movies:
            return Record.commonValues(*[self._movies[m] for m in movies])
        else:
            return N.array(self._users.keys(), dtype=USER_ID_TYPECODE)
        
    _MovieRecordType = UnratedMovieRecord
    _UserRectordType = UnratedUserRecord


class RatedDataset(Dataset):

    def iterMoviesUsersRatings(self, **min_max_ratings):
        '''Return an iterator over all (movie,user,rating) tuples of this dataset.'''
        enum_movies = enumerate(self._movies)
        enum_movies.next() # ignore the dummy movie
        for movie_id,movie in enum_movies:
            for user_id, rating in movie.iterValueRatings(**min_max_ratings):
                yield (movie_id, user_id, rating)

    def movies(self, *users, **min_max_ratings):
        '''Return an array of the movie IDs rated by the given user(s).
        
        If no users are given, return all the movie IDs of this dataset.
        Otherwise, return the IDs of the movies that have been rated by ALL the
        given users.
        '''
        if users:
            return RatedRecord.commonValues(*[self._users[u] for u in users],
                                            **min_max_ratings)
        else: return Dataset.movies(self)

    def users(self, *movies, **min_max_ratings):
        '''Return an array of the user IDs that rated the given movie(s).
        
        If no movies are given, return all the user IDs of this dataset.
        Otherwise, return the IDs of the users that have rated ALL the given movies.
        '''
        if movies:
            return RatedRecord.commonValues(*[self._movies[m] for m in movies],
                                            **min_max_ratings)
        else: return Dataset.users(self)

    def rmse(self, predictor):
        s,n = 0.0,0
        for movie,user,rating in self.iterMoviesUsersRatings():
            d = predictor(movie,user) - rating
            s += d*d
            n += 1
        return (s/n) ** 0.5

    #---- ratings accessors and iterators for a single movie or user -----------
    
    def movieRatings(self, movie, **min_max_ratings):
        '''Return an array of the given movie's ratings.'''
        return self._movies[int(movie)].ratings(**min_max_ratings)

    def userRatings(self, user, **min_max_ratings):
        '''Return an array of the given user's ratings.'''
        return self._users[user].ratings(**min_max_ratings)
    
    def iterRatedUsers(self, movie, **min_max_ratings):
        '''Return an iterator over all (user,rating) pairs for the given movie.'''
        return self._movies[movie].iterValueRatings(**min_max_ratings)
        
    def iterRatedMovies(self, user, **min_max_ratings):
        '''Return an iterator over all (movie,rating) pairs for the given user.'''
        return self._users[user].iterValueRatings(**min_max_ratings)
    
    #---- ratings accesors and iterators for jointly rated movies and users ----
    
    def jointRatedMovieMatrix(self, *movies, **min_max_ratings):
        '''Return the ratings of the users that rated ALL the given movies.
        
        Return a 2-D array whose [i,j] element is the rating of the i-th movie
        by the j-th user returned from self.users(*movies).
        '''
        movies = [self._movies[m] for m in movies]
        return RatedRecord.jointRatings(*movies, **min_max_ratings)

    def jointRatedUserMatrix(self, *users, **min_max_ratings):
        '''Return the ratings of the movies that were rated by ALL the given users.
        
        Return a 2-D array whose [i,j] element is the rating of the i-th user
        to the j-th movie returned from self.movies(*users).
        '''
        users = [self._users[u] for u in users]
        return RatedRecord.jointRatings(*users, **min_max_ratings)
            
    def iterJointlyRatedUsers(self, *movies, **min_max_ratings):
        '''Return an iterator over (user,ratings) pairs for each user that rated
        ALL the given movies. 'ratings' is a len(movies) 1-D array.
        '''
        movies = [self._movies[m] for m in movies]
        return RatedRecord.iterValueRatings(*movies, **min_max_ratings)
    
    def iterJointlyRatedMovies(self, *users, **min_max_ratings):
        '''Return an iterator over (movie,ratings) pairs for each movie rated by
        ALL the given users. 'ratings' is a len(users) 1-D array.
        '''
        users = [self._users[u] for u in users]
        return RatedRecord.iterValueRatings(*users, **min_max_ratings)
        
    _MovieRecordType = RatedMovieRecord
    _UserRectordType = RatedUserRecord


##class MovieInfo(object):
##    pass


def writePredictionFile(infile, outfile, predictor, format='%.3f'):
    from setup import iterQset
    f = open(outfile, 'w')
    last_movie_id = None
    for movie_id,user_id in iterQset(infile):
        if movie_id != last_movie_id:
            print >> f, '%d:' % movie_id
            last_movie_id = movie_id
        print >> f, format % predictor(movie_id,user_id)
    f.close()
        
    


if __name__ == '__main__':
    import sys
    d = RatedDataset(sys.argv[1])
    predictor = lambda m,u: 3.6
    print d.rmse(predictor)
    ##writePredictionFile(sys.argv[1], 'dummy.txt', predictor)
    
    #for m,u,r in d.iterMoviesUsersRatings():
        #print m,u,r

    #from setup import timeCall    
    #from itertools import islice
    #movies = list(islice(MovieRatings.fromfile(sys.argv[1]), 13))[11:]
    #dicts = [dict(m.iterValueRatings()) for m in movies]
    #c = MovieRatings.commonValues(*movies)
    #print c
    #print sorted(set(m1.values()) & set(m2.values()))
    ##print MovieRatings.jointRatings(*movies)# list(Movie.iter_common_values_ratings(m1,m2))
    #print [d1[k] for k in c]
    #print [d2[k] for k in c]
