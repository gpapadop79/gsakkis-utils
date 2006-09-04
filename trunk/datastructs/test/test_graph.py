#!/usr/bin/env python

import unittest,copy
from common import sorted, uniq
from datastructs.graph import Digraph, MultiDigraph, GraphEdge

__author__ = "George Sakkis <gsakkis@rutgers.edu>"


#======= Digraph tests =======================================================

class GraphTestCase(unittest.TestCase):
    graph_class = Digraph
    all_edges = [GraphEdge(i,j) for (i,j) in
                 (1,2),(1,3),(2,4),(2,3),(4,2),(5,5),(2,4)]
    edges = uniq(all_edges)
    extra_nodes = [3,6]
    nodes = uniq(extra_nodes + [e.startNode for e in edges] +
                 [e.endNode for e in edges])

    next_edges_2 = (GraphEdge(2,4), GraphEdge(2,3))
    previous_edges_4 = [GraphEdge(2,4)]

    def getGraph(self):
        return self.graph_class(nodes=self.extra_nodes, edges=self.all_edges)

    #------- node accesor tests ----------------------------------------------

    def test_numNodes(self):
        self.assertEquals(self.getGraph().numNodes(), 6)

    def test_hasNode(self):
        hasNode = self.getGraph().hasNode
        self.failUnless(hasNode(5))
        self.failUnless(hasNode(6))
        self.failIf(hasNode('a'))

    def test_nodes(self):
        self.assertEqualSets(self.getGraph().nodes(), self.nodes)

    def test_iterNodes(self):
        iterNodes = self.getGraph().iterNodes
        self.failUnless(3 in iterNodes())
        self.failIf('a' in iterNodes())
        it = iterNodes()
        self.failUnless(list(it))
        # iterator is exhausted
        self.failIf(list(it))

    def test_nextNodes(self, nextNodes=None):
        if nextNodes is None:
            nextNodes = self.getGraph().nextNodes
        self.assertEqualSets(nextNodes(1), [2,3])
        self.assertEqualSets(nextNodes(2), [3,4])
        self.assertEqualSets(nextNodes(3), [])
        self.assertEqualSets(nextNodes(4), [2])
        self.assertEqualSets(nextNodes(5), [5])
        self.assertEqualSets(nextNodes(6), [])
        self.assertRaises(KeyError,nextNodes,'a')

    def test_iterNextNodes(self):
        iterNextNodes = self.getGraph().iterNextNodes
        it = iterNextNodes(2)
        self.failUnless(list(it))
        # iterator is exhausted
        self.failIf(list(it))
        # assert that list(iterNextNodes) == nextNodes
        self.test_nextNodes(lambda node: list(iterNextNodes(node)))

    def test_previousNodes(self, previousNodes=None):
        if previousNodes is None:
            previousNodes = self.getGraph().previousNodes
        self.assertEqualSets(previousNodes(1), [])
        self.assertEqualSets(previousNodes(2), [1,4])
        self.assertEqualSets(previousNodes(3), [1,2])
        self.assertEqualSets(previousNodes(4), [2])
        self.assertEqualSets(previousNodes(5), [5])
        self.assertEqualSets(previousNodes(6), [])
        self.assertRaises(KeyError,previousNodes,'a')

    def test_iterPreviousNodes(self):
        iterPreviousNodes = self.getGraph().iterPreviousNodes
        it = iterPreviousNodes(3)
        self.failUnless(list(it))
        # iterator is exhausted
        self.failIf(list(it))
        # assert that list(iterPreviousNodes) == previousNodes
        self.test_previousNodes(lambda node: list(iterPreviousNodes(node)))

    #------- edge accesor tests ----------------------------------------------

    def test_numEdges(self):
        self.assertEquals(self.getGraph().numEdges(), len(self.edges))

    def test_hasEdge(self):
        hasEdge = self.getGraph().hasEdge
        self.failUnless(hasEdge(GraphEdge(1,2)))
        self.failUnless(hasEdge((1,2)))
        self.failUnless(hasEdge((5,5)))
        self.failIf(hasEdge((2,1)))

    def test_edges(self):
        self.assertEqualSets(self.getGraph().edges(), self.edges)

    def test_iterEdges(self):
        iterEdges = self.getGraph().iterEdges
        self.failUnless(GraphEdge(1,2) in iterEdges())
        self.failIf(GraphEdge(2,1) in iterEdges())
        it = iterEdges()
        self.failUnless(list(it))
        # iterator is exhausted
        self.failIf(list(it))

    def test_nextEdges(self, nextEdges=None):
        if nextEdges is None:
            nextEdges = self.getGraph().nextEdges
        self.assertEqualSets(nextEdges(1), [GraphEdge(1,2), GraphEdge(1,3)])
        self.assertEqualSets(nextEdges(2), self.next_edges_2)
        self.assertEqualSets(nextEdges(3), [])
        self.assertEqualSets(nextEdges(4), [GraphEdge(4,2)])
        self.assertEqualSets(nextEdges(5), [GraphEdge(5,5)])
        self.assertEqualSets(nextEdges(6), [])
        self.assertRaises(KeyError,nextEdges,'a')

    def test_iterNextEdges(self):
        iterNextEdges = self.getGraph().iterNextEdges
        it = iterNextEdges(2)
        self.failUnless(list(it))
        # iterator is exhausted
        self.failIf(list(it))
        # assert that list(iterNextEdges) == nextEdges
        self.test_nextEdges(lambda node: list(iterNextEdges(node)))

    def test_previousEdges(self, previousEdges=None):
        if previousEdges is None:
            previousEdges = self.getGraph().previousEdges
        self.assertEqualSets(previousEdges(1), [])
        self.assertEqualSets(previousEdges(2), [GraphEdge(1,2),
                                                GraphEdge(4,2)])
        self.assertEqualSets(previousEdges(3), [GraphEdge(1,3),
                                                GraphEdge(2,3)])
        self.assertEqualSets(previousEdges(4), self.previous_edges_4)
        self.assertEqualSets(previousEdges(5), [GraphEdge(5,5)])
        self.assertEqualSets(previousEdges(6), [])
        self.assertRaises(KeyError,previousEdges,'a')

    def test_iterPreviousEdges(self):
        iterPreviousEdges = self.getGraph().iterPreviousEdges
        it = iterPreviousEdges(4)
        self.failUnless(list(it))
        # iterator is exhausted
        self.failIf(list(it))
        # assert that list(iterPreviousEdges) == previousEdges
        self.test_previousEdges(lambda node: list(iterPreviousEdges(node)))

    #------- (in)equality, copy tests ----------------------------------------

    def test_eq(self):
        g1 = self.getGraph()
        g2 = self.getGraph()
        self.assertEquals(g1,g2)
        self.assertNotEquals(g1,self.graph_class())
        edges = [(1,2),(1,3),(2,3),(2,4)]
        self.assertEquals(Digraph(edges), MultiDigraph(edges))
        edges.append(GraphEdge(2,3))
        self.assertNotEquals(Digraph(edges), MultiDigraph(edges))

    def test_copy(self):
        g = self.getGraph()
        c = copy.copy(g)
        self.assertEquals(c,g)

    def test_copy_modify(self):
        mutations = [('addNode', 'a'), ('removeNode', 4),
                     ('addEdge', (1,5)), ('addEdge', (1,2)),
                     ('removeEdge', (1,2)), ('removeEdge', (2,4))]
        # assert that the clone does not change after mutating the original
        for method,arg in mutations:
            orig = self.getGraph()
            clone = copy.copy(orig)
            getattr(orig,method)(arg,False)
            self.assertEqualSets(clone.nodes(), self.nodes)
            self.assertEqualSets(clone.edges(), self.edges)
        # assert that the original does not change after mutating the clone
        for method,arg in mutations:
            orig = self.getGraph()
            clone = copy.copy(orig)
            getattr(clone,method)(arg,False)
            self.assertEqualSets(orig.nodes(), self.nodes)
            self.assertEqualSets(orig.edges(), self.edges)

    #def test_deepcopy(self):
    #    warnings.warn("missing test for deepcopy")

    #------- node mutator tests ----------------------------------------------

    def test_addNode(self):
        safe = False
        self._addNode(safe)
        # add an existing node; nothing changes
        g=self.getGraph(); g.addNode(3,safe)
        self.assertEqualSets(g.edges(), self.edges)
        self.assertEqualSets(g.nodes(), self.nodes)

    def test_addNode_safe(self):
        safe = True
        self._addNode(safe)
        # try to add an exsting node
        self.assertRaises(KeyError, self.getGraph().addNode, 3, safe)

    def test_removeNode(self):
        self._removeNode(True)
        # try to remove an inexistent node
        self.assertRaises(KeyError, self.getGraph().removeNode, 'a')

    def test_removeNode_unsafe(self):
        self._removeNode(False)
        # try to remove an inexistent node
        g=self.getGraph(); g.removeNode('a', safe=False)
        self.assertEqualSets(g.nodes(), self.nodes)
        self.assertEqualSets(g.edges(), self.edges)

    def test_popNode(self):
        g = self.getGraph()
        node = g.popNode()
        self.assertEqualSets(g.nodes(), self._restNodes(node))
        self.assertEqualSets(g.edges(), self._restEdges_removedNodes(node))
        # try to pop from an empty graph
        self.assertRaises(KeyError, self.graph_class().popNode)

    def test_clearNodes(self):
        g = self.getGraph()
        g.clearNodes()
        self.failIf(g.nodes())
        self.failIf(g.edges())
        self.assertEquals(g, self.graph_class())

    #------- edge mutator tests ----------------------------------------------

    def test_addEdge_new(self):
        safe = False
        # add a new edge among the existing nodes
        g = self.getGraph(); g.addEdge((1,5), safe)
        self.assertEqualSets(g.nodes(), self.nodes)
        self.assertEqualSets(g.edges(), self.edges + [GraphEdge(1,5)])
        # add a new edge and one new node
        g = self.getGraph(); g.addEdge((1,'a'), safe)
        self.assertEqualSets(g.nodes(), self.nodes + ['a'])
        self.assertEqualSets(g.edges(), self.edges + [GraphEdge(1,'a')])
        g = self.getGraph(); g.addEdge(('a',5), safe)
        self.assertEqualSets(g.nodes(), self.nodes + ['a'])
        self.assertEqualSets(g.edges(), self.edges + [GraphEdge('a',5)])
        # add a new edge and two new nodes
        g = self.getGraph(); g.addEdge(('a','b'), safe)
        self.assertEqualSets(g.nodes(), self.nodes + ['a','b'])
        self.assertEqualSets(g.edges(), self.edges + [GraphEdge('a','b')])

    def test_addEdge_new_safe(self):
        safe = True
        # add a new edge among the existing nodes
        g = self.getGraph(); g.addEdge((1,5), safe)
        self.assertEqualSets(g.nodes(), self.nodes)
        self.assertEqualSets(g.edges(), self.edges + [GraphEdge(1,5)])
        # try to a new edge to an inexistent node
        self.assertRaises(KeyError, self.getGraph().addEdge, (1,'a'), safe)
        self.assertRaises(KeyError, self.getGraph().addEdge, ('a',5), safe)
        self.assertRaises(KeyError, self.getGraph().addEdge, ('a','b'), safe)

    def test_addEdge_existing(self):
        g = self.getGraph(); g.addEdge((1,2), False)
        self.assertEqualSets(g.nodes(), self.nodes)
        self.assertEqualSets(g.edges(), self.edges)
        self.assertRaises(KeyError, self.getGraph().addEdge, (1,2), True)

    def test_removeEdge(self):
        self._removeEdge(True)
        # try to remove an inexistent edge
        for edge in GraphEdge(2,5), GraphEdge(2,'a'), GraphEdge('a',5):
            self.assertRaises(KeyError, self.getGraph().removeEdge, edge)

    def test_removeEdge_unsafe(self):
        self._removeEdge(False)
        # try to remove an inexistent edge
        for edge in GraphEdge(2,5), GraphEdge(2,'a'), GraphEdge('a',5):
            g = self.getGraph(); g.removeEdge(edge, safe=False)
            self.assertEqualSets(g.nodes(), self.nodes)
            self.assertEqualSets(g.edges(), self.edges)

    def test_popEdge(self):
        g = self.getGraph()
        edge = g.popEdge()
        self.assertEqualSets(g.nodes(), self.nodes)
        self.assertEqualSets(g.edges(), self._restEdges_removedEdges(edge))
        # try to pop from an empty graph
        self.assertRaises(KeyError, self.graph_class().popNode)

    def test_clearEdges(self):
        g = self.getGraph()
        g.clearEdges()
        self.assertEqualSets(g.nodes(), self.nodes)
        self.failIf(g.edges())

    #------- helpers ---------------------------------------------------------

    def assertEqualSets(self,c1,c2):
        #self.assertEquals(list(c1), list(c2))
        self.assertEquals(sorted(c1), sorted(c2))

    def _addNode(self,safe):
        # add a new node
        g = self.getGraph(); g.addNode('a',safe)
        self.assertEqualSets(g.edges(), self.edges)
        self.assertEqualSets(g.nodes(), list(self.nodes) + ['a'])

    def _removeNode(self, safe):
        g = self.getGraph(); g.removeNode(4,safe)
        self.assertEqualSets(g.nodes(), self._restNodes(4))
        self.assertEqualSets(g.edges(), self._restEdges_removedNodes(4))

    def _removeEdge(self, safe):
        for edge in GraphEdge(1,2), GraphEdge(2,4):
            g = self.getGraph(); g.removeEdge(edge,safe)
            self.assertEqualSets(g.nodes(), self.nodes)
            self.assertEqualSets(g.edges(), self._restEdges_removedEdges(edge))

    def _restNodes(self,*removedNodes):
        rest = list(self.nodes)
        for removedNode in removedNodes:
            rest.remove(removedNode)
        return rest

    def _restEdges_removedNodes(self, *removedNodes):
        return filter(lambda edge: (edge.startNode not in removedNodes
                                    and edge.endNode not in removedNodes),
                      self.edges)

    def _restEdges_removedEdges(self, *removedEdges):
        # remove all duplicates of each removedEdge
        return filter(lambda edge: edge not in removedEdges, self.edges)


#======= MultiDigraph tests ==================================================

class DigraphTestCase(GraphTestCase, unittest.TestCase):
    graph_class = MultiDigraph

    edges = GraphTestCase.all_edges
    next_edges_2 = (GraphEdge(2,4), GraphEdge(2,3), GraphEdge(2,4))
    previous_edges_4 = (GraphEdge(2,4), GraphEdge(2,4))

    def test_addEdge_existing(self):
        for safe in False,True:
            g = self.getGraph(); g.addEdge((1,2),safe)
            self.assertEqualSets(g.nodes(), self.nodes)
            self.assertEqualSets(g.edges(), self.edges + [GraphEdge(1,2)])

    def _restEdges_removedEdges(self, *removedEdges):
        # remove only one duplicate of each removedEdge
        rest = list(self.edges)
        for removedEdge in removedEdges:
            rest.remove(removedEdge)
        return rest


#=============================================================================

if __name__ == '__main__':
    unittest.main()
