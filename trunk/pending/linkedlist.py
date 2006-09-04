# todo:
# - refactoring,unittest,documentation,benchmark

from itertools import izip

__author__ = "George Sakkis <gsakkis@rutgers.edu>"
__all__ = ["LinkedList"]


class LinkedList(object):
    __slots__ = '_start', '_end', '_size'

    #------- constructor / destructor ----------------------------------------

    def __init__(self,sequence=()):
        self._size = 0
        self._start = self._end = None
        self += sequence

    def __del__(self):
        current = self._start
        while current != None:
            # cut the link to the previous node so that this can be released
            current.previous = None
            current = current.next

    #------- accesors --------------------------------------------------------

    def __len__(self):
        return self._size

    def __iter__(self):
        current = self._start
        while current != None:
            yield current.item
            current = current.next

    def __getitem__(self,index):
        if not isinstance(index,slice):
            return self._getnode(index).item
        else:  # slice object
            result = LinkedList()
            for i in self._iterslice(index):
                result.append(i.item)
            return result

    def count(self,item):
        counter = 0
        for i in self:
            if i==item: counter +=1
        return counter

    def index(self,item):
        counter = 0
        for i in self:
            if i==item: return counter
            counter += 1
        selftype = _typename(self)
        raise ValueError("%s.index(x): x not in list" % _typename(self))

    #------- factories -------------------------------------------------------

    def __add__(self,other):
        if isinstance(other,LinkedList):
            result = LinkedList(self)
            result += other
            return result
        else:
            selftype = _typename(self)
            raise TypeError('can only concatenate %s (not "%s") to '
                            '%s' % (selftype,_typename(other),selftype))

    def __mul__(self,num):
        if not isinstance(num,int):
            raise TypeError("can't multiply sequence to non-int")
        result = LinkedList(self)
        result *= num
        return result

    #------- mutators --------------------------------------------------------

    def __setitem__(self,index,item):
        if not isinstance(index,slice):
            self._getnode(index).item = item
        else:  # slice object
            try:
                if index.step == None:  # non extended slice
                    sliceiter = self._iterslice(index)
                    seqiter = iter(item)
                    currentNode = None
                    while True:
                        try:
                            currentNode = sliceiter.next()
                            try: # perform assignments as long as both
                                 # iterators are not done
                                currentItem = seqiter.next()
                                currentNode.item = currentItem
                            except StopIteration:
                                # seqiter.next() is done; remove the rest
                                # nodes returned by sliceiter
                                self._removenode(currentNode)
                        except StopIteration: # sliceiter.next() is done
                             # insert the rest items returned by seqiter
                            if currentNode!=None: # non-empty slice
                                while True:
                                    try:
                                        currentItem = seqiter.next()
                                        self._insertnode(currentItem,
                                                         currentNode,
                                                         setAfter=True)
                                        currentNode = currentNode.next
                                    except StopIteration: return
                            else: # empty slice
                                size = self._size
                                start = index.start!=None and index.start or 0
                                if start < 0: start += size
                                if start > size: start = size
                                elif start < 0: start = 0
                                while True:
                                    try:
                                        currentItem = seqiter.next()
                                        self.insert(start, currentItem)
                                        start += 1
                                    except StopIteration: return
                else:   # extended slice
                    slicenodes = list(self._iterslice(index))
                    if len(slicenodes) != len(item):
                        raise ValueError("attempt to assign sequence of size "
                                         "%d to extended slice of size %d" %
                                         (len(item),len(slicenodes)))
                    else:
                        it = iter(slicenodes)
                        for i in item: it.next().item = i
            except TypeError:
                raise TypeError('must assign sequence (not "%s") to slice'
                                % _typename(item))

    def __delitem__(self,index):
        if not isinstance(index,slice):
            self.pop(index)
        else:  # slice object
            for node in self._iterslice(index): self._removenode(node)

    def __iadd__(self,other):
        for item in other: self.append(item)
        return self

    extend = __iadd__

    def __imul__(self,num):
        if not isinstance(num,int):
            raise TypeError("can't multiply sequence to non-int")
        initSize = self._size
        num -= 1
        for i in xrange(num):
            it = iter(self)
            for j in xrange(initSize):
                self.append(it.next())
        return self

    def append(self,item):
        self._insertnode(item,self._end,setAfter=True)

    def insert(self,index,item):
        try:
            next = self._getnode(index)
            self._insertnode(item,next,setAfter=False)
        except IndexError:
            if index >= self._size: self.append(item)
            else: self.insert(0,item)

    def pop(self,index=-1):
        node = self._getnode(index)
        self._removenode(node)
        return node.item

    def remove(self,item):
        for node in self._iternode():
            if node.item==item: return self._removenode(node)
        raise ValueError("%s.remove(x): x not in list" % _typename(self))

    def reverse(self):
        middle = self._size // 2
        bottom = self._start; top = self._end
        for i in xrange(middle):
            tmp = top.item
            top.item = bottom.item
            bottom.item = tmp
            bottom = bottom.next; top = top.previous

    def sort(self,f=cmp):
        array = list(self)
        array.sort(f)
        i = 0
        for node in self._iternode():
            node.item = array[i]
            i += 1

    #------- (in)equality, str, repr -----------------------------------------

    def __eq__(self,other):
        if not isinstance(other,LinkedList) or len(self) != len(other):
            return False
        for i,j in izip(self,other):
            if i!=j:
                return False
        return True

    def __ne__(self,other):
        return not self.__eq__(other)

    def __str__(self):
        return "[%s]" % ', '.join(map(repr,self))

    def __repr__(self):
        return "LinkedList(%s)" % self

    #------- 'private' members -----------------------------------------------

    def _getnode(self,index):
        if isinstance(index,int):
            if index < 0: index += self._size
            if 0 <= index < self._size:
                current = self._start
                for i in xrange(index): current = current.next
                return current
            else:
                raise IndexError("list index out of range")
        else:
            raise TypeError("list indices must be integer")

    def _insertnode(self,item,node,setAfter):
        if node==None:
            newnode = self._Node(item,prevNode=None,nextNode=None)
        else:
            if setAfter:
                newnode = self._Node(item,prevNode=node,nextNode=node.next)
            else:
                newnode = self._Node(item,prevNode=node.previous,nextNode=node)
        if newnode.previous==None: self._start = newnode
        if newnode.next==None: self._end = newnode
        self._size += 1

    def _removenode(self,node):
        if node.previous==None: # first Node
            self._start = node.next
        else:                   # non-first Node
            node.previous.next = node.next
        if node.next==None:     # last Node
            self._end = node.previous
        else:                   # non-last Node
            node.next.previous = node.previous
        self._size -= 1

    def _iternode(self):
        current = self._start
        while current != None:
            yield current
            current = current.next

    def _iterslice(self,slice):
        start,stop,step = slice.indices(len(self))
        #print start,stop,step
        if step > 0:
            updateNode = lambda node: node.next
        else:
            updateNode = lambda node: node.previous
        if (stop-start)*step <= 0:
            return
        stop = abs(start-stop)
        step = abs(step)
        currentNode = self._getnode(start)
        currentIndex = 0;
        while currentIndex < stop:
            if currentIndex % step == 0:
                yield currentNode
            currentNode = updateNode(currentNode)
            currentIndex += 1

    class _Node(object):

        __slots__ = 'item', 'next', 'previous'

        def __init__(self,item,nextNode=None,prevNode=None):
            self.item = item
            self.next = nextNode
            self.previous = prevNode
            if nextNode!=None: nextNode.previous = self
            if prevNode!=None: prevNode.next = self
        #def __del__(self): print "deleting", self


def _typename(obj):
    '''Return the name of the object's type.'''
    try: return obj.__class__.__name__
    except AttributeError:
        return type(obj).__name__
