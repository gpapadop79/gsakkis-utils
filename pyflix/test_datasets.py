import sys
import numpy as N
from pyflix.datasets import UnratedDataset, RatedDataset


def almost_equals(a,b,e=1e-3):
    return N.allclose(a,b,e)


class TestQualifyingDataset(object):
    disabled = True

    def setup_class(cls):
        cls.data = UnratedDataset('bin/qualifying_set')
        cls.num_instances = 2817131
    
    def test_movies(self):
        get_movies = self.data.movies
        movies = get_movies()
        assert len(movies) == 17470 and min(movies) == 1 and max(movies) == 17770        
        assert set(get_movies(169978)) == set([11647,16380,1865,3282,4590,
                                                     5807,6475,8393])
        assert set(get_movies(481,198627)) == set([528,9458])
    
    def test_users(self):
        get_users = self.data.users
        users = get_users()
        assert len(users) == 478615 and min(users) == 6 and max(users) == 2649429
        users = get_users(1234)
        assert len(users) == 88 and min(users) == 25118 and max(users) == 2634849
        assert set(get_users(5,197)) == set([1244207, 1369939, 1561430, 1987416,
                                             2296800])
    
    def test_iterMoviesUsers(self):
        movies = set(self.data.movies())
        users = set(self.data.users())
        s = 0
        for m,u in self.data.iterMoviesUsers():
            assert m in movies and u in users
            s += 1
        assert s == self.num_instances


class TestTrainingDataset(object):
    disabled = False
    
    def setup_class(cls):
        cls.data = RatedDataset('bin/training_set')
        cls.num_instances = 99072112
    
    def test_movies(self):
        get_movies = self.data.movies
        movies = get_movies()
        assert len(movies) == 17770 and min(movies) == 1 and max(movies) == 17770
        movies = get_movies(169978)
        assert len(movies) == 111 and min(movies) == 30 and max(movies) == 17580         
        assert set(get_movies(1048577,2097163)) == set([5496, 12317, 15205, 16384])

    def test_users(self):
        get_users = self.data.users
        users = get_users()
        assert len(users) == 480189 and min(users) == 6 and max(users) == 2649429
        users = get_users(1234)
        assert len(users) == 3238 and min(users) == 793 and max(users) == 2648869
        users = get_users(5,197)
        assert len(users) == 406 and min(users) == 11186 and max(users) == 2647871

    #def test_iterMoviesUsers(self):
    #    TestQualifyingDataset.test_iterMoviesUsers(self)
            
    def test_ratingsTo(self):
        get_ratings = self.data.ratingsTo
        assert almost_equals(N.average(get_ratings(567)), 2.8171)
        assert almost_equals(N.average(get_ratings(567, min_rating=4)), 4.0857)
        assert almost_equals(N.average(get_ratings(567, max_rating=3)), 2.5)

    def test_ratingsBy(self):
        get_ratings = self.data.ratingsBy
        assert almost_equals(N.average(get_ratings(213317)), 4.6154)
        assert almost_equals(N.average(get_ratings(213317, min_rating=4)), 4.75)
        assert almost_equals(N.average(get_ratings(213317, max_rating=4)), 3.75)
    
    def test_iterUsersRatings(self):
        movie_id = 567
        users,ratings = zip(*self.data.iterUsersRatings(movie_id))
        assert users == tuple(self.data.users(movie_id))
        assert ratings == tuple(self.data.ratingsTo(movie_id))

    def test_iterMoviesRatings(self):
        user_id = 213317
        movies,ratings = zip(*self.data.iterMoviesRatings(user_id))
        assert movies == tuple(self.data.movies(user_id))
        assert ratings == tuple(self.data.ratingsBy(user_id))
    
    def test_ratingsMatrixTo(self):
        movie_ratings = self.data.ratingsMatrixTo(5,198)
        assert almost_equals(N.average(movie_ratings[:,0]), 3.2222)
        assert almost_equals(N.average(movie_ratings[:,1]), 2.6667)
    
    def test_ratingsMatrixBy(self):
        user_ratings = self.data.ratingsMatrixBy(1048577,2097163)
        assert almost_equals(N.average(user_ratings[:,0]), 4.5)
        assert almost_equals(N.average(user_ratings[:,1]), 2.75)
    
    def test_iterJointUsersRatings(self):
        movie_ids = 5,198
        users,rating_arrays = zip(*self.data.iterJointUsersRatings(*movie_ids))
        assert users == tuple(self.data.users(*movie_ids))
        assert N.alltrue(N.array(rating_arrays) == self.data.ratingsMatrixTo(*movie_ids))
    
    def test_iterJointMoviesRatings(self):
        user_ids = 1048577,2097163
        movies,rating_arrays = zip(*self.data.iterJointMoviesRatings(*user_ids))
        assert movies == tuple(self.data.movies(*user_ids))
        assert N.alltrue(N.array(rating_arrays) == self.data.ratingsMatrixBy(*user_ids))


class TestProbeDataset(object):
    pass
