import sys
import heapq

__all__ = ['topsort', 'CycleException']

class CycleException(Exception): pass


def itertopsort(sequences):
    graph = seqsToGraph(sequences)
    sorted = []
    queue = []
    indegrees = {}
    for v in graph.iterVertices():
        deg = graph.inDegree(v)
        if deg == 0:
            queue.append(v)
        else:
            indegrees[v] = deg
    return _itertopsort(graph,queue,indegrees)


def _itertopsort(graph, queue, indegrees):
    if not queue:
        if indegrees:
            raise CycleException()
        yield []
    else:
        for i,v in enumerate(queue):
            new_indegrees = indegrees.copy()
            new_queue = [x for j,x in enumerate(queue) if j!=i]
            for w in graph.nextVertices(v):
                #print v,w
                new_indegrees[w] -= 1
                if new_indegrees[w] == 0:
                    new_queue.append(w)
                    del new_indegrees[w]
            ##print v,new_queue,new_indegrees
            for subresult in _itertopsort(graph,new_queue,new_indegrees):
                yield [v] + subresult



def topsort(sequences):
    graph = seqsToGraph(sequences)
    isVisited = set()
    isSorted = set()
    sorted = []
    for v in graph.iterVertices():
        if not v in isVisited:
            _topsort(v, graph, isVisited, isSorted, sorted)
    sorted.reverse()
    return sorted

def _topsort(v, graph, isVisited, isSorted, sorted):
    isVisited.add(v)
    for w in graph.nextVertices(v):
        if not w in isVisited:
            _topsort(w, graph, isVisited, isSorted, sorted)
        elif not w in isSorted:
            raise CycleException()
    sorted.append(v)
    isSorted.add(v)


def seqsToGraph(sequences):
    '''Convert an iterable of partially ordered sequences into a Graph.'''
    from itertools import chain,islice,izip
    # take the union of all elements
    vertices = set(chain(*sequences))
    edges = set()
    for seq in sequences:
        # form consecutive pairs (x1,x2),(x2,x3),...(xN-1,xN) from a sequence
        edges.update(izip(seq,islice(seq,1,None)))
    return Graph(edges,vertices)


class Graph(object):
    def __init__(self, edges, vertices=None):
        self._vertices = V = set()
        if vertices is not None:
            V.update(vertices)
        for v,w in edges:
            V.add(v); V.add(w)
        self._forward = forward = dict((v,set()) for v in V)
        self._backward = backward = dict((v,set()) for v in V)
        for v,w in edges:
            forward[v].add(w)
            backward[w].add(v)

    def iterVertices(self):
        return iter(self._vertices)

    def iterEdges(self):
        for v, neighbors in self._forward.iteritems():
            for w in neighbors:
                yield v,w

    def nextVertices(self, v):
        return iter(self._forward[v])

    def outDegree(self, v):
        return len(self._forward[v])

    def inDegree(self, v):
        return len(self._backward[v])



if __name__ == '__main__':
    #print topsort(['abdcbe', 'be'])
    #for s in itertopsort(['za', 'ab', 'bc', 'ca']):
    for s in itertopsort(['bcd', 'dc']):
        print s
    #print topsort(['ab', 'bc', 'bd', 'de', 'ef', 'dc'])
    #for seqs in (['ab', 'bc', 'bd', 'de', 'ef', 'dc'],
    #             ['ab', 'bc', 'bd', 'de', 'ef', 'dc', 'g'],
    #             ['ab', 'bc', 'ca']):
    #    #print 'A:', topsort(seqs)
    #    print 'B:', itertopsort(seqs)
    #    print
