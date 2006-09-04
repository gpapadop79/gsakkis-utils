'''A disjoint-sets implementation as a union-find data structure.'''

__author__ = "George Sakkis <gsakkis@rutgers.edu>"
__all__ = ["UnionFind"]


class UnionFind:
    '''A union-find data structure.
    
    The union-find data structure represents a collection of disjoint sets of
    hashable objects. It provides efficient amortized performance on computing
    the L{union} of two or more sets B{in-place}. No other set operation except
    for union is implemented by this class; however L{getSet} can be called to
    get a L{sets.Set} instance representing the set an item belongs to.
    '''
    
    def __init__(self):
        '''Create an empty union find data structure.'''
        self._ranks = {}
        # self._parents: maps each object to its parent in the union-find forest
        self._parents = {}
        # self._descendants: maps each object that is currently a root in the
        # the union-find forest to the list of its descendants
        self._descendants = {}
    
    def add(self, *objects):
        '''Add each object in a new singleton set.
        
        It has no effect on objects already in this UnionFind.
        @return: self
        '''
        for object in objects:
            if object not in self._parents:
                self._parents[object] = object
                self._ranks[object] = 0
        return self
    
    def inSameSet(self, *objects):
        '''Check if all the objects are in the same set.
        
        @raise KeyError: If any object is not in this UnionFind.
        @rtype: bool
        '''
        if objects:
            parent = self[objects[0]]
            for object in objects[1:]:
                if self[object] != parent:
                    return False
        return True
        
    def __len__(self):
        '''Return the number of elements in this UnionFind.'''
        return len(self._parents)
    
    def __iter__(self):
        '''Return an iterator over the elements of this UnionFind.'''
        return iter(self._parents)
        
    def numSets(self):
        '''Return the number of sets in this UnionFind.'''
        return len(self._ranks)
    
    def iterSets(self):
        '''Return an iterator over the disjoint sets of this UnionFind.'''
        return iter([self.getSet(x) for x in self._ranks])
    
    def getSet(self,object):
        '''Return the set that the given object belongs to.
        
        @raise KeyError: If the object is not in this UnionFind.
        @rtype: sets.Set
        '''
        import sets
        parent = self[object]
        set = sets.Set(self._descendants[parent])
        set.add(parent)
        return set

    def __getitem__(self, object):
        '''Find the representative of the set that the object is in.
        
        The object must be hashable.
        @raise KeyError: If the object is not in this UnionFind.
        '''
        pathToRoot = []; current = object
        while True:
            parent = self._parents[current]
            if parent == current:
                break
            pathToRoot.append(current)
            current = parent
        for node in pathToRoot:
            self._parents[node] = current
        self._descendants.setdefault(current,[]).extend(pathToRoot)
        return current
    
    def __str__(self):
        return ", ".join(["%s->%s" % pair
                          for pair in self._parents.iteritems()])

    def union(self, *objects):
        '''Join the sets that contain the given objects.
        
        Any object that is not in this UnionFind is first L{added <add>}.
        All objects must be hashable.
        @return: self
        '''
        size = len(objects)
        if size == 0:
            return self
        elif size == 1:
            return self.add(objects[0])
        elif size == 2:
            return self._union(*objects)
        else:
            # divide & conquer: split into the two groups, unite each of
            # them separately and finally unite the two groups
            middle = size/2
            self.union(*objects[:middle])
            self.union(*objects[middle:])
            return self._union(objects[0],objects[-1])
    
    def _union(self, object1, object2):
        '''Join the sets that contain the two objects.
        
        Any object that is not in this UnionFind is first L{added <add>}.
        The objects must be hashable.
        @return: self
        '''
        # make sure the objects are in this UnionFind
        for object in object1,object2:
            if object not in self:
                self.add(object)
        highRankedRoot,lowRankedRoot = self[object1],self[object2]
        if highRankedRoot != lowRankedRoot:
            highRank,lowRank = self._ranks[highRankedRoot],self._ranks[lowRankedRoot]
            if lowRank > highRank:
                highRankedRoot,lowRankedRoot = lowRankedRoot,highRankedRoot
            self._parents[lowRankedRoot] = highRankedRoot
            self._descendants[highRankedRoot].append(lowRankedRoot)
            try:
                lowChildren = self._descendants.pop(lowRankedRoot)
                self._descendants[highRankedRoot] += lowChildren
            except KeyError: pass
            if lowRank == highRank:
                self._ranks[highRankedRoot] += 1
            del self._ranks[lowRankedRoot]
        return self
