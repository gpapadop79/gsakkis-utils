__all__ = ['AbstractConfusionMatrix', 'SingleConfusionMatrix', 'MultiConfusionMatrix']

import Numeric as Num
from itertools import imap


#====== AbstractConfusionMatrix ================================================

class AbstractConfusionMatrix(object):

    def __init__(self, classes):
        '''Create an empty confusion matrix.

        @param classes: An iterable over categories (labels).
        '''
        self._classes = tuple(classes)
        self._class2matrix = dict((c,Num.zeros((2,2))) for c in self._classes)
        # the sum of all matrices; used for the microaveraging metrics
        self._sum = Num.zeros((2,2))

    def classes(self):
        return self._classes

    def set_from_array(self, array):
        '''Set the confusion matrix from a 2D Numeric array (matrix).

        The A[i,j] cell of the array is the number of instances classified as
        class-i that belong to class-j.

        @param array: A |C|x|C| Numeric array (where C is the set of categories).
        '''
        size = len(self._classes)
        if Num.shape(array) != (size,size):
            raise ValueError('Wrong array size: %s' % str(Num.shape(array)))
        for i,pred in enumerate(self._classes):
            for j,real in enumerate(self._classes):
                self.add_event(real,pred,array[i,j])

    def add_event(self, real, pred, n=1):
        '''Update the confusion matrix with an event of classifying C{n}
        instances of class C{real} to class C{pred}.
        '''
        raise NotImplementedError('Abstract method')

    #------- metrics -----------------------------------------------------------

    # most metrics follow the same template, so create them dynamically
    for metric in 'accuracy', 'precision', 'recall', 'fallout', 'generality':
        args = (metric,metric)
        # per class metric
        exec '''def %s(self, c):
                    try: return _%s(self._class2matrix[c])
                    except ZeroDivisionError: return None''' % args
        # microaveraging metric
        exec '''def micro_%s(self):
                    try: return _%s(self._sum)
                    except ZeroDivisionError: return None''' % args
        # macroaveraging metric
        exec '''def macro_%s(self):
                    cs = self._classes
                    # filter out the classes whose metric is undefined
                    values = [x for x in imap(self.%s,cs) if x is not None]
                    try: return (sum(values) / len(values))
                    except ZeroDivisionError: return None''' % args
    del metric,args

    # f_score is special in that it takes an extra parameter apart from the class
    def f_score(self, c, b=1):
        try: return _f_score(self._class2matrix[c], b)
        except ZeroDivisionError: return None
    def micro_f_score(self, b=1):
        try: return _f_score(self._sum, b)
        except ZeroDivisionError: return None
    def macro_f_score(self, b=1):
        cs = self._classes
        # filter out the classes whose f_score is undefined
        values = [x for x in (self.f_score(c,b) for c in cs) if x is not None]
        try: return sum(values) / len(values)
        except ZeroDivisionError: return None

    def dump(self):
        table = []
        metrics = ['generality', 'accuracy', 'precision', 'recall', 'fallout',
                   'f_score']
        # header
        table.append(['']+metrics)
        # per class metrics
        for c in self.classes():
            row = [c]
            for name in metrics:
                row.append(getattr(self,name)(c))
            table.append(row)
        # averaging metrics
        for prefix in 'macro', 'micro':
            row = [prefix+' average']
            for name in metrics:
                row.append(getattr(self,'%s_%s' %(prefix,name))())
            table.append(row)
        # format numeric cells
        for row in table:
            for j,cell in enumerate(row):
                if isinstance(cell, float):
                    row[j] = '%.2f%%' % (cell*100)
        return _pretty_print(table)

# ---- metrics defined on a 2x2 matrix -----------------------------------------

def _accuracy(m):
    correct = float(m[0,0]+m[1,1])
    return correct / (correct+m[1,0]+m[0,1])

def _precision(m):
    hits = float(m[0,0])
    return hits / (hits+m[0,1])

def _recall(m):
    hits = float(m[0,0])
    return hits / (hits+m[1,0])

def _fallout(m):
    noise = float(m[0,1])
    return noise / (noise+m[1,1])

def _f_score(m, b=1):
    hits = float(m[0,0])
    p = hits / (hits+m[0,1])
    r = hits / (hits+m[1,0])
    b2 = b*b
    return (b2+1)*r*p / (b2*p+r)

def _generality(m):
    relevant = float(m[0,0]+m[1,0])
    return relevant / (relevant+m[0,1]+m[1,1])


#====== SingleConfusionMatrix ==================================================

class SingleConfusionMatrix(AbstractConfusionMatrix):
    '''Confusion matrix for single-label categorization.

    An event consists of a (real,pred) tuple: each instance belongs to a single
    class C{real} and it is classified in a single class C{pred}.
    '''

    def add_event(self, real, pred, n=1):
        c2m = self._class2matrix.copy()
        summed = self._sum
        if real == pred: # hit; update the true positives
            c2m.pop(real)[0,0] += n
            summed[0,0] += n
        else: # miss
            # update the false positives for the predicted category
            c2m.pop(pred)[0,1] += n
            summed[0,1] += n
            # update the false negatives for the real category
            c2m.pop(real)[1,0] += n
            summed[1,0] += n
        # update the true negative for all other categories
        for m in c2m.itervalues():
            m[1,1] += n
        summed[1,1] += n*len(c2m)
        assert Num.allclose(self._sum, sum(self._class2matrix.itervalues()))

    @classmethod
    def test(cls):
        cm = cls(['yes', 'no', 'maybe'])
        #               real
        # pred  |  yes    no    maybe
        #------------------------------------
        # yes   |  21      7      3
        # no    |   3     38      6
        # maybe |   5      4     19
        cm.set_from_array(Num.array([[21,7,3],[3,38,6],[5,4,19]]))
        return cm


#====== MultiConfusionMatrix ===================================================

class MultiConfusionMatrix(AbstractConfusionMatrix):
    '''Confusion matrix for multi-label categorization.

    An event consists of a (real*,pred*) tuple: each instance belongs to zero or
    more classes C{real*} and it is classified to zero or more classes C{pred*}.
    '''

    def add_event(self, real, pred, n=1):
        '''Update the confusion matrix with an event of classifying C{n}
        instances of class(es) C{real} to class(es) C{pred}.

        @param real,pred: Either a single category or a sequence (list,tuple,set)
            of categories.
        '''
        real,pred = map(_make_set, (real,pred))
        for c,m in self._class2matrix.iteritems():
            if c in pred:
                if c in real:
                    cell = 0,0
                else:
                    cell = 0,1
            else:
                if c in real:
                    cell = 1,0
                else:
                    cell = 1,1
            m[cell] += n
            self._sum[cell] += n

    @classmethod
    def test(cls):
        cm = cls(['yes', 'no', 'maybe'])
        cm.add_event(['yes'], ['yes', 'no'],2)
        cm.add_event(['no','maybe'], 'no',3)
        return cm

def _make_set(arg):
    if not isinstance(arg, (set,frozenset)):
        if not isinstance(arg,(tuple,list)):
            arg = [arg]
        arg = frozenset(arg)
    return arg

#====== _pretty_print ==========================================================

try:
    from common.indent import indent
except ImportError:
    from pprint import pprint as _pretty_print
else:
    def _pretty_print(table):
        return indent(table, hasHeader=True)


##====== SingleConfusionMatrix_old =============================================
#
#class SingleConfusionMatrix_old(object):
#
#    def __init__(self, classes):
#        self._classes = tuple(classes)
#        self._class2Index = dict((c,i) for i,c in enumerate(self._classes))
#        size = len(self._class2Index)
#        self._matrix = Num.zeros((size,size))
#
#    def classes(self):
#        return self._classes
#
#    def __getitem__(self, (real,pred)):
#        return self._matrix[self._class2Index[real], self._class2Index[pred]]
#
#    def __setitem__(self, (real,pred), n):
#        self._matrix[self._class2Index[real], self._class2Index[pred]] = n
#
#    def add_event(self, real, pred, n=1):
#        self._matrix[self._class2Index[real], self._class2Index[pred]] += n
#
#    def set_from_array(self, array):
#        assert Num.shape(array) == Num.shape(self._matrix)
#        self._matrix[:] = array
#
#    #------- per class metrics -------------------------------------------------
#
#    def accuracy(self, c):
#        sum = Num.sum
#        m = self._matrix; i = self._class2Index[c]
#        return 1 - float(sum(m[i,:]) + sum(m[:,i]) - 2*m[i,i]) / sum(sum(m))
#
#    def precision(self, c):
#        m = self._matrix; i = self._class2Index[c]
#        return float(m[i,i]) / Num.sum(m[i,:])
#
#    def recall(self, c):
#        m = self._matrix; i = self._class2Index[c]
#        return float(m[i,i]) / Num.sum(m[:,i])
#
#    def fallout(self, c):
#        sum = Num.sum
#        m = self._matrix; i = self._class2Index[c]
#        return float(sum(m[i,:]) - m[i,i]) / (sum(sum(m)) - sum(m[:,i]))
#
#    def f_score(self, c, b=1):
#        r,p = self.recall(c), self.precision(c)
#        b2 = b*b
#        return (b2+1)*r*p / (b2*p+r)
#
#    def generality(self, c):
#        sum = Num.sum
#        m = self._matrix; i = self._class2Index[c]
#        return float(sum(m[:,i])) / sum(sum(m))
#
#    # most macroaveraging metrics follow the same template, so create them dynamically
#    for metric in 'accuracy', 'precision', 'recall', 'fallout', 'generality':
#        exec '''def macro_%s(self):
#                    cs = self._classes
#                    return (sum(self.%s(c) for c in cs) / len(cs))''' % (metric,metric)
#    del metric
#
#    # f_score is special in that it takes an extra parameter apart from the class
#    def macro_f_score(self, b=1):
#        cs = self._classes; return sum(self.f_score(c,b) for c in cs) / len(cs)



if __name__ == '__main__':
    from pprint import pprint
    for cls in SingleConfusionMatrix,MultiConfusionMatrix:
        cm = cls.test()
        pprint(cm._class2matrix)
        print cm.dump()
        print
