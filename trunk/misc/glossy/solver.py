import sys
from glossy import Problem #,Page,Picture

class Solver(object):

    def __init__(self, problem):
        self._problem = problem
        print problem.page

    #def _initPlace(self):
    #    for picture in self._problem.pictures:


if __name__ == '__main__':
    s = Solver(Problem(sys.argv[1]))

