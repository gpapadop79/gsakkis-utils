'''Module for representing various classes of graphs.

A graph node (vertex) can be any hashable object. An edge graph is represented
as a L{GraphEdge} instance. For convenience, all methods that expect edges can
also accept iterables of two elements (startNode,endNode) that are wrapped
into L{GraphEdge} instances.

@sort: Digraph, MultiDigraph, GraphEdge, graph2dot
@requires: python 2.3
@todo: deepcopy
'''

import copy
from sets import Set
from itertools import imap,chain
#from datastructs.multiset import MultiSet

__author__ = "George Sakkis <gsakkis@rutgers.edu>"
__all__ = ["GraphEdge", "Digraph", "MultiDigraph", "graph2dot"]

#======= GraphEdge ===========================================================

class GraphEdge(object):
    '''Representation of a graph edge.

    The endpoints of a GraphEdge are immutable.
    '''

    __slots__ = ['__start', '__end']

    def __init__(self, start, end):
        '''
        @param start: The source node of this edge.
        @param end: The destination node of this edge.
        '''
        self.__start = start
        self.__end = end

    startNode = property(lambda self: self.__start,
                         doc="The source node of this edge")
    endNode   = property(lambda self: self.__end,
                         doc="The destination node of this edge")

    def __repr__(self):
        return repr((self.startNode,self.endNode))

    def __hash__(self):
        return hash((self.startNode, self.endNode))

    def __eq__(self,other):
        try: return self.startNode == other.startNode \
                    and self.endNode == other.endNode
        except AttributeError:
            return False

    def __ne__(self,other):
        return not self.__eq__(other)

    def __cmp__(self,other):
        try: return cmp(self.startNode,other.startNode) \
                    or cmp(self.endNode,other.endNode)
        except AttributeError:
            raise TypeError("Cannot compare %s with %s" %
                            (type(self), type(other)))

#======= Digraph =============================================================

class Digraph(object):
    '''Directed graph representation.

    @group Node Accesors: nodes, numNodes, hasNode, nextNodes, previousNodes,
        iterNodes, iterNextNodes, iterPreviousNodes
    @group Edge Accesors: edges, numEdges, hasEdge, nextEdges, previousEdges,
        iterEdges, iterNextEdges, iterPreviousEdges
    @group Node Mutators: addNode, removeNode, popNode, clear, clearNodes
    @group Edge Mutators: addEdge, removeEdge, popEdge, clearEdges
    @group Miscellaneous: copy, __copy__, __eq__, __ne__, __str__
    '''

    __slots__ = ['_nodes', '_edges', '_prevEdges']

    def __init__(self, edges=(), nodes=()):
        '''
        @param edges: An iterable of L{edges <GraphEdge>} or (start,end)
            iterables.
        @param nodes: An iterable of nodes. This is necessary only for
            solitary nodes (i.e nodes not attached to any edge specified in
            C{edges}.
        '''
        # the set of nodes for this graph
        self._nodes = Set()
        # dict mapping each node to the Set of next adjacent edges
        self._edges = {}
        # dict mapping each node to the Set of previous adjacent edges
        self._prevEdges = {}
        for node in nodes: self.addNode(node,False)
        for edge in edges: self.addEdge(edge,False)

    #------- node accesors ---------------------------------------------------

    def nodes(self):
        '''Return this graph's nodes.
        @rtype: sets.Set of nodes
        '''
        return Set(self.iterNodes())

    def numNodes(self):
        '''Return the number of this graph's nodes.
        @rtype: int
        '''
        return len(self._nodes)

    def hasNode(self, node):
        '''Check whether the given node is in this graph.
        @rtype: bool
        '''
        return node in self._nodes

    def nextNodes(self, node):
        '''Return the nodes linked by the specified node.
        @rtype: sets.Set of nodes
        '''
        return Set(self.iterNextNodes(node))

    def previousNodes(self, node):
        '''Return the nodes linked to the specified node.
        @rtype: sets.Set of nodes
        '''
        return Set(self.iterPreviousNodes(node))

    def iterNodes(self):
        '''Return an iterator over this graph's nodes.'''
        return iter(self._nodes)

    def iterNextNodes(self, node):
        '''Return an iterator over the nodes linked by the specified node.'''
        return imap(lambda edge: edge.endNode, self.iterNextEdges(node))

    def iterPreviousNodes(self, node):
        '''Return an iterator over the nodes linked to the specified node.'''
        return imap(lambda edge: edge.startNode, self.iterPreviousEdges(node))

    #------- edge accesors ---------------------------------------------------

    def edges(self):
        '''Return this graph's edges.
        @rtype: sets.Set of L{edges <GraphEdge>}
        '''
        return Set(self.iterEdges())

    def numEdges(self):
        '''Return the number of this graph's edges.
        @rtype: int
        '''
        return sum(imap(len, self._edges.itervalues()))

    def hasEdge(self,edge):
        '''Check whether the given edge is in this graph.
        @rtype: bool
        '''
        edge = _adapt(edge)
        try:
            return edge in self._edges[edge.startNode]
        except KeyError:
            return False

    def nextEdges(self, node):
        '''Return the outcoming edges of the given node.
        @rtype: sets.Set of L{edges <GraphEdge>}
        '''
        return Set(self.iterNextEdges(node))

    def previousEdges(self, node):
        '''Return the incoming edges of the given node.
        @rtype: sets.Set of L{edges <GraphEdge>}
        '''
        return Set(self.iterPreviousEdges(node))

    def iterEdges(self):
        '''Return an iterator over this graph's edges.'''
        return chain(*imap(iter,self._edges.itervalues()))

    def iterNextEdges(self, node):
        '''Return an iterator over the outcoming edges of this node.'''
        try: return iter(self._edges[node])
        except KeyError:
            if node in self._nodes: return iter(())
            else: raise

    def iterPreviousEdges(self, node):
        '''Return an iterator over the incoming edges of this node.'''
        try: return iter(self._prevEdges[node])
        except KeyError:
            if node in self._nodes: return iter(())
            else: raise

    #------- miscellaneous ---------------------------------------------------

    def __eq__(self,other):
        try:
            #todo: remove sorted() once MultiDigraph.edges returns Multiset
            #      instead of list
            from common import sorted
            return self.nodes() == other.nodes() \
                   and sorted(self.edges()) == sorted(other.edges())
        except AttributeError:
            return False

    def __ne__(self,other):
        return not self.__eq__(other)

    def copy(self):
        clone = self.__class__()
        cp = copy.copy
        clone._nodes = cp(self._nodes)
        # copy the edge Set of each node
        for newDict,oldDict in [(clone._edges,self._edges),
                                (clone._prevEdges,self._prevEdges)]:
            for node,edgeSet in oldDict.iteritems():
                newDict[node] = cp(edgeSet)
        return clone

    __copy__ = copy  # for the copy module

    def __str__(self):
        nodes = ", ".join(imap(str,self.iterNodes()))
        edges = ", ".join(["%s->%s" % (edge.startNode,edge.endNode)
                           for edge in self.iterEdges()])
        return "graph {nodes:{%s}, edges:{%s}}" % (nodes,edges)

    #------- node mutators ---------------------------------------------------

    def addNode(self, node, safe=False):
        '''Add the given node to this graph.
        @raise KeyError: If C{safe} is True and C{node} is already in the graph.
        '''
        if safe and node in self._nodes:
            raise KeyError("Node %s is already in the graph" % node)
        self._nodes.add(node)

    def removeNode(self, node, safe=True):
        '''Remove the given node and all the edges attached to it from this graph.
        @raise KeyError: If C{safe} is True and C{node} is not in the graph.
        '''
        try:
            # 1. remove every adjacent edge
            for getEdges in self.nextEdges, self.previousEdges:
                for edge in getEdges(node):
                    self.removeEdge(edge)
            # 2. delete the node from _nodes
            self._nodes.remove(node)
        except KeyError:
            if safe: raise
        # 3. delete the node from _edges, _prevEdges
        for edges in self._edges, self._prevEdges:
            try: del edges[node]
            except KeyError: pass

    def popNode(self):
        '''Remove a "random" node and all the edges attached to it.
        @return: The removed node.
        @raise KeyError: If the graph is empty.
        '''
        try:
            node = self.iterNodes().next()
        except StopIteration:
            raise KeyError("graph is empty")
        self.removeNode(node)
        return node

    def clearNodes(self):
        '''Remove all the nodes and edges of this graph.'''
        self._edges = {}
        self._prevEdges = {}
        self._nodes = Set()

    clear = clearNodes

    #------- edge mutators ---------------------------------------------------

    def addEdge(self, edge, safe=False):
        '''Add the given edge to this graph.
        @raise KeyError: If C{safe} is True and either C{edge} is already in
            the graph, or any (or both) of the C{edge}'s endpoints are not in
            the graph.
        '''
        edge = _adapt(edge)
        start,end = edge.startNode, edge.endNode
        if safe:
            if start not in self._nodes:
                raise KeyError("Node %s is not in the graph" % start)
            if end not in self._nodes:
                raise KeyError("Node %s is not in the graph" % end)
        nextEdges = self._edges.setdefault(start,Set())
        previousEdges = self._prevEdges.setdefault(end,Set())
        if safe and (edge in nextEdges or edge in previousEdges):
            raise KeyError("Edge %s is already in the graph" % edge)
        self._nodes.add(start)
        self._nodes.add(end)
        nextEdges.add(edge)
        previousEdges.add(edge)

    def removeEdge(self, edge, safe=True):
        '''Remove the given edge from this graph.
        @raise KeyError: If C{safe} is True and C{edge} is not in the graph.
        '''
        edge = _adapt(edge)
        start,end = edge.startNode, edge.endNode
        try:
            self._edges[start].remove(edge)
            try: self._prevEdges[end].remove(edge)
            except KeyError:
                raise AssertionError("Should never reach here; inconsistent "
                                     "self._edges and self._prevEdges")
        except KeyError:
            if safe: raise

    def popEdge(self):
        '''Remove and return a "random" edge from this graph.
        @return: The removed edge.
        @raise KeyError: If the graph has no edges.
        '''
        try:
            edge = self.iterEdges().next()
        except StopIteration:
            raise KeyError("graph has no edges")
        self.removeEdge(edge)
        return edge

    def clearEdges(self):
        '''Remove all the edges of this graph.'''
        for edges in self._edges,self._prevEdges:
            for edgeSet in edges.itervalues():
                edgeSet.clear()

#======= MultiDigraph ========================================================

class MultiDigraph(Digraph):
    '''Directed graph that allows multiple edges between two nodes.

    @group Node Accesors: nodes, numNodes, hasNode, nextNodes, previousNodes,
        iterNodes, iterNextNodes, iterPreviousNodes
    @group Edge Accesors: edges, numEdges, hasEdge, nextEdges, previousEdges,
        iterEdges, iterNextEdges, iterPreviousEdges
    @group Node Mutators: addNode, removeNode, popNode, clear, clearNodes
    @group Edge Mutators: addEdge, removeEdge, popEdge, clearEdges

    @todo: make L{edges}, L{nextEdges}, L{previousEdges} return MultiSet
        instead of list once there is a stable MultiSet class.
    '''

    __slots__ = []

    #------- node accesors ---------------------------------------------------

    def iterNextNodes(self, node):
        try: return self._edges[node].iterkeys()
        except KeyError:
            if node in self._nodes: return iter(())
            else: raise

    def iterPreviousNodes(self, node):
        try: return self._prevEdges[node].iterkeys()
        except KeyError:
            if node in self._nodes: return iter(())
            else: raise

    #------- edge accesors ---------------------------------------------------

    def edges(self):
        return list(self.iterEdges())

    def numEdges(self):
        count = 0
        for neighbors in self._edges.itervalues():
            count += sum(imap(len,neighbors.itervalues()))
        return count

    def hasEdge(self,edge):
        edge = _adapt(edge)
        try:
            return edge in self._edges[edge.startNode][edge.endNode]
        except KeyError:
            return False

    def nextEdges(self, node):
        return list(self.iterNextEdges(node))

    def previousEdges(self, node):
        return list(self.iterPreviousEdges(node))

    def iterEdges(self):
        for neighbors in self._edges.itervalues():
            for edgeSet in neighbors.itervalues():
                for edge in edgeSet:
                    yield edge
        # equivalent obscure expression using itertools
        #return chain(*imap(
        #    lambda neighborsDict: chain(*neighborsDict.itervalues()),
        #    self._edges.itervalues()))

    def iterNextEdges(self, node):
        try:
            next = self._edges[node]
        except KeyError:
            if node in self._nodes: return iter(())
            else: raise
        else:
            return chain(*imap(iter,next.itervalues()))

    def iterPreviousEdges(self, node):
        try:
            previous = self._prevEdges[node]
        except KeyError:
            if node in self._nodes: return iter(())
            else: raise
        else:
            return chain(*imap(iter,previous.itervalues()))

    #------- copy ------------------------------------------------------------

    def copy(self):
        clone = Digraph.copy(self)
        cp = copy.copy
        # copy the edge lists
        for fromDict in clone._edges, clone._prevEdges:
            for toDict in fromDict.itervalues():
                for toNode,edgeList in toDict.iteritems():
                    toDict[toNode] = cp(edgeList)
        return clone

    __copy__ = copy  # for the copy module

    #------- edge mutators ---------------------------------------------------

    def addEdge(self, edge, safe=False):
        edge = _adapt(edge)
        start,end = edge.startNode, edge.endNode,
        if safe:
            if start not in self._nodes:
                raise KeyError("Node %s is not in the graph" % start)
            if end not in self._nodes:
                raise KeyError("Node %s is not in the graph" % end)
        self._edges.setdefault(start,{}).setdefault(end,[]).append(edge)
        self._prevEdges.setdefault(end,{}).setdefault(start,[]).append(edge)
        self._nodes.add(start)
        self._nodes.add(end)

    def removeEdge(self,edge,safe=True):
        edge = _adapt(edge)
        start,end = edge.startNode, edge.endNode,
        try:
            self._edges[start][end].remove(edge)
            try: self._prevEdges[end][start].remove(edge)
            except KeyError:
                # bring into consistent state and re-raise the error
                self._edges.setdefault(start,{}).setdefault(end,[]).append(edge)
                raise
        except KeyError:
            if safe: raise

#======= graph2dot ===========================================================

def graph2dot(graph, graphprops={}, nodeprops={}, edgeprops={}, name=None):
                                                #edgeformat='\t"%s" -> "%s"'):
    from cStringIO import StringIO
    out = StringIO()
    print >> out, 'digraph %s {\n' % (name is None and "G" or name)
    for (d,label) in [(graphprops,"graph"),
                      (nodeprops,"node"),
                      (edgeprops,"edge")]:
        if d:
            items = ", ".join(["\t%s=%s" % (k,v) for (k,v) in d.iteritems()])
            print >> out, '%s [%s]\n' % (label,items)
    for edge in graph.iterEdges():
        print >> out, "\t%s->%s" % (edge.startNode,edge.endNode)
    print >> out, "}\n"
    return out.getvalue()

#======= GraphEdge adaptor ===================================================

def _adapt(edge):
    return isinstance(edge,GraphEdge) and edge or GraphEdge(*edge)
