#!/usr/bin/env python

import numpy as N
from pyflix.algorithms import Algorithm


class MovieAverage(Algorithm):
    '''Baseline algorithm that computes the average of all the votes for a movie
    and predicts that for any user.

    This algorithm will return a RMSE score of 1.0528 on the scrubbed dataset.
    '''

    def __init__(self, training_set):
        self._movie_averages = {}
        super(MovieAverage,self).__init__(training_set)
        
    def __call__(self, movie_id, user_id):
        try: return self._movie_averages[movie_id]
        except KeyError:
            avg = N.average(self._training_set.ratingsTo(movie_id))
            self._movie_averages[movie_id] = avg
            return avg


class UserAverage(Algorithm):
    '''Baseline algorithm that computes the average of all the votes for a user
    and predicts that for any movie.

    This algorithm will return a RMSE score of 1.0688 on the scrubbed dataset.
    '''

    def __init__(self, training_set):
        self._user_averages = {}
        super(UserAverage,self).__init__(training_set)
        
    def __call__(self, movie_id, user_id):
        try: return self._user_averages[user_id]
        except KeyError:
            avg = N.average(self._training_set.ratingsBy(user_id))
            self._user_averages[user_id] = avg
            return avg


class DoubleAverage(MovieAverage,UserAverage):
    '''Computes the average of MovieAverage and UserAverage.
    
    This algorithm will return a RMSE score of 1.0158 on the scrubbed dataset.
    '''

    def __call__(self, movie_id, user_id):
        return (MovieAverage.__call__(self,movie_id,user_id) +
                UserAverage.__call__(self,movie_id,user_id)) / 2
