import sys
from itertools import imap,chain
from copy import copy,deepcopy
from cStringIO import StringIO
from sets import Set

from datastructs.multiset import MultiSet

__author__ = "George Sakkis <gsakkis@rutgers.edu>"
__all__ = ["GraphEdge", "Digraph", "MultiDigraph"]

        
################################# GraphEdge #################################

class GraphEdge(object):
    def __init__(self, start=None, end=None):
        self._start = start
        self._end = end
        
    startNode = property(lambda self: self._start)
    endNode   = property(lambda self: self._end)

    def __repr__(self):
        return repr((self.startNode,self.endNode))
    def __hash__(self):
        return hash((self.startNode, self.endNode))
    def __eq__(self,other):
        return self.startNode == other.startNode and \
               self.endNode == other.endNode

################################# Digraph #################################

class Digraph(object):
    def __init__(self, edges=[], nodes=[], name=None):
        self.name = name
        # self._nodes the set of nodes for this graph
        self._nodes = Set()
        # self._edges: dict mapping each node to the Set of next adjacent edges
        self._edges = {}
        # self._edges: dict mapping each node to the Set of previous adjacent edges
        self._prevEdges = {}
        for node in nodes: self.addNode(node)
        for edge in edges: self.addEdge(edge)

    ############# accessors #############

    def numNodes(self): 
        return len(self._nodes)
    def numEdges(self): 
        return sum(imap(len, self._edges.itervalues()))
    def hasNode(self,node): 
        return node in self._nodes
    def hasEdge(self,edge):
        edge = self._normalize(edge)
        try:             
            return edge in self._edges[edge.startNode]
        except KeyError: 
            return False                
    
    def nodes(self): 
        return Set(self.iterNodes())
    def edges(self): 
        return Set(self.iterEdges())    
    def nextNodes(self,node): 
        return Set(self.iterNextNodes(node))
    def nextEdges(self,node):
        return Set(self.iterNextEdges(node))  
    def previousNodes(self,node): 
        return Set(self.iterPreviousNodes(node))
    def previousEdges(self,node): 
        return Set(self.iterPreviousEdges(node))        

    def iterNodes(self): 
        return iter(self._nodes)    
    def iterEdges(self):
        return chain(*imap(iter,self._edges.itervalues()))
    def iterNextNodes(self,node): 
        for edge in iter(self._edges[node]):
            yield edge.endNode
    def iterNextEdges(self,node): 
        return iter(self._edges[node])
    def iterPreviousNodes(self,node): 
        for edge in iter(self._prevEdges[node]):
            yield edge.startNode
    def iterPreviousEdges(self,node): 
        return iter(self._prevEdges[node])
                    
    def __ne__(self,other): 
        return not self == other
    def __eq__(self,other):
        try:    return self._edges == other._edges
        except: return False
    
    def __copy__(self): 
        cp = self.__class__(name=self.name)
        cp._nodes = copy(self._nodes)
        # copy the edge Set for each node
        for newDict,oldDict in (cp._edges,self._edges), (cp._prevEdges,self._prevEdges):
            for node,edgeSet in oldDict.iteritems():
                newDict[node] = copy(edgeSet)
        return cp

    def __str__(self):
        nodes = ", ".join(imap(str,self.iterNodes()))
        edges = ", ".join(self._str())
        return "graph %s {nodes:{%s}, edges:{%s}}" % (self.name,nodes,edges)

    def str2dot(self, graphprops={}, nodeprops={}, edgeprops={}, edgeformat='\t"%s" -> "%s"\n'):
        ref = sys.stdout
        sys.stdout = StringIO()
        print 'digraph %s {\n' % (self.name is None and "G" or self.name)
        for (d,label) in (graphprops,"graph"), (nodeprops,"node"), (edgeprops,"edge"):
            if d:
                items = ", ".join(["\t%s=%s" % (k,v) for (k,v) in d.iteritems()])
                print '%s [%s]\n' % (label,items)
        for edge in self._str():
            print "\t%s" % edge
        print "}\n"
        sys.stdout,ref = ref,sys.stdout
        return ref.getvalue()
        
    ############# mutators #############
        
    def addNode(self,node): 
        self._nodes.add(node)                
        for dict in self._edges,self._prevEdges:
            dict.setdefault(node,Set())

    def removeNode(self,node): 
        self._nodes.discard(node)
        # remove every adjacent edge
        for edge in self.nextEdges(node):
            self.removeEdge(edge)
        for edge in self.previousEdges(node):
            self.removeEdge(edge)
        del self._edges[node]
        del self._prevEdges[node]
    
    def popNode(self): 
        try:
            node = self.iterNodes().next()
        except StopIteration: 
            raise KeyError, "graph is empty"
        self.removeNode(node)
        return node
        
    def addEdge(self,edge):
        edge = self._normalize(edge)
        start,end = edge.startNode, edge.endNode
        self._edges.setdefault(start,Set()).add(edge)
        self._prevEdges.setdefault(end,Set()).add(edge)
        self._nodes.add(start)
        self._nodes.add(end)
    
    def removeEdge(self,edge):
        edge = self._normalize(edge)
        try: 
            self._edges[edge.startNode].discard(edge)
            self._prevEdges[edge.endNode].discard(edge)
        except KeyError: 
            pass    
        
    def popEdge(self):
        try: 
            edge = self.iterEdges().next()
        except StopIteration: 
            raise KeyError, "edge set is empty"
        self.removeEdge(edge)
        return edge
    
    def clear(self):
        self._edges = {}
        self._prevEdges = {}
        self._nodes = Set()

    def clearEdges(self):
        for dict in self._edges,self._prevEdges:
            for node in dict:
                dict[node] = Set()

    ############# 'protected' methods #############
    
    def _str(self, edgeformat="%s->%s"):
        return [edgeformat % (edge.startNode,edge.endNode) 
                for edge in self.iterEdges()]
    
    def _normalize(self, edge):
        if isinstance(edge,GraphEdge):
            return edge
        return GraphEdge(edge[0], edge[1])
    
        
############################ MultiDigraph #############################
    
class MultiDigraph(Digraph):
    
    def __init__(self, edges=[], nodes=[], name=None):
        super(MultiDigraph,self).__init__(edges,nodes,name)
    
    def nodes(self): 
        return MultiSet(self.iterNodes())
    def edges(self): 
        return MultiSet(self.iterEdges())    
    def nextNodes(self,node): 
        return MultiSet(self.iterNextNodes(node))
    def nextEdges(self,node):
        return MultiSet(self.iterNextEdges(node))  
    def previousNodes(self,node): 
        return MultiSet(self.iterPreviousNodes(node))
    def previousEdges(self,node): 
        return MultiSet(self.iterPreviousEdges(node))        

    def numEdges(self): 
        count = 0
        for neighbors in self._edges.itervalues():
            count += sum(imap(len,neighbors.itervalues()))
        return count
    
    def hasEdge(self,edge):
        edge = self._normalize(edge)
        try:             
            return edge in self._edges[edge.startNode][edge.endNode]
        except KeyError: 
            return False                

    def iterEdges(self):
        for prev,neighbors in self._edges.iteritems():
            for next,edgeSet in neighbors.iteritems():
                for edge in edgeSet:
                    yield edge
    
    def iterNextNodes(self,node):
        for next,edgeSet in self._edges[node].iteritems():
            for _ in xrange(len(edgeSet)):
                yield next
    
    def iterPreviousNodes(self,node): 
        for prev,edgeSet in self._prevEdges[node].iteritems():
            for _ in xrange(len(edgeSet)):
                yield prev
    
    def iterNextEdges(self,node): 
        return chain(*imap(iter,self._edges[node].itervalues()))
    
    def iterPreviousEdges(self,node): 
        return chain(*imap(iter,self._prevEdges[node].itervalues()))
    
    def __copy__(self): 
        cp = super(MultiDigraph,self).__copy__()
        # copy the edge lists
        for dict in self._edges, self._prevEdges:
            for neighbors in dict.itervalues():
                for node,edgeList in neighbors.iteritems():
                    neighbors[node] = copy(edgeList)
        return cp
            
    ############# mutators #############
                  
    def addNode(self,node): 
        self._nodes.add(node)
        for dict in self._edges, self._prevEdges:
            dict.setdefault(node,{})

    def addEdge(self,edge):
        edge = self._normalize(edge)
        start,end = edge.startNode, edge.endNode, 
        self._edges.setdefault(start,{}).setdefault(end,[]).append(edge)
        self._prevEdges.setdefault(end,{}).setdefault(start,[]).append(edge)
        self._nodes.add(start)
        self._nodes.add(end)

    def removeEdge(self,edge):
        edge = self._normalize(edge)
        try: 
            self._edges[edge.startNode][edge.endNode].remove(edge)
            self._prevEdges[edge.endNode][edge.startNode].remove(edge)
        except (KeyError,ValueError): 
            pass

    def clearEdges(self):
        for dict in self._edges,self._prevEdges:
            for node in dict:
                dict[node] = {}

