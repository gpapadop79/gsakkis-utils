import sys
from inspect import isclass
from pyflix.path import path
from pyflix.datasets import RatedDataset, writePredictions


class Algorithm(object):
    def __init__(self, training_set):
        self._training_set = training_set
        
    def __call__(self, movie_id, user_id):
        raise NotImplementedError('Abstract method')


def run(basedir, *algorithms):
    training_set = RatedDataset(basedir/'training_set')
    probe_set = RatedDataset(basedir/'probe_set')
    for algorithm in algorithms:
        if isinstance(algorithm, basestring): # qualified class name
            algorithm = import_name(algorithm)
        name = algorithm.__name__
        if isclass(algorithm):
            algorithm = algorithm(training_set)
        print '%s.%s: %.4f' % (algorithm.__module__, name,
                               probe_set.rmse(algorithm,progressbar=True))

def import_name(name):
    try: mod = __import__(name)
    except ImportError:
        if '.' not in name: raise
        mod = __import__(name[:name.rindex('.')])
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


if __name__ == '__main__':
    run(path(sys.argv[1]), *sys.argv[2:])
