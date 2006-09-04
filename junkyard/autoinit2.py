

class AssertInit(type):
    """Assert that initializers get called.

    Set this as a __metaclass__ for the root class
    in a class hierarchy, and you will get AssertionError
    if some of the base class initializers isn't called.
    """
    _has_real_init = {}

    def __new__(cls, classname, bases, classdict):
        old_init = classdict.get('__init__', lambda self: None)

        def new_init(self, *args, **kwargs):
            # here selfclass refers to the class in which
            # this __init__ function lies (see below this function
            # definition for the definition of selfclass)

            if hasattr(self, '_visited_bases'):
                self._visited_bases[selfclass] = True
                old_init(self, *args, **kwargs)
                return

            # initialize _visited_bases_ by scanning *all* superclasses
            # and by creating mappings from the class object to False
            # if the base class needs to be visited, True otherwise.
            self._visited_bases = vb = {}
            for claz in filter(AssertInit._has_real_init.get,
                               selfclass.__mro__[1:]):
                vb[claz] = not hasattr(claz,'__init__')
            
            old_init(self, *args, **kwargs)

            # scan _visited_bases_ to see which base class
            # initializers didn't get visited
            for superclass, visited in vb.iteritems():
                if not visited:
                    print "unvisited:", superclass
                    old_superclass_init = getattr(superclass,'__init__')
                    def new_superclass_init(self,*args,**kwds):
                        super(claz,self).__init__()
                        old_superclass_init(self,*args,**kwds)
                    setattr(claz,'__init__',new_superclass_init)
            #unvisited = ['%s.%s' % (claz.__module__, claz.__name__)
            #             for claz, visited in vb.items() if not visited]
            #if unvisited:
            #    fullClassName = '%s.%s' %\
            #                    (selfclass.__module__, selfclass.__name__)
            #
            #    raise AssertionError("Initializer%s in class%s (%s) not "
            #                         "visited when constructing object "
            #                         "from class %s" %
            #                         (len(unvisited) > 1 and 's' or '',
            #                          len(unvisited) > 1 and 'es' or '',
            #                          ', '.join(unvisited),
            #                          fullClassName))            
            delattr(self,'_visited_bases')
        # ^def new_init
        
        has_real_init = '__init__' in classdict
        classdict['__init__'] = new_init
        # the newly created class, selfclass, is referred to inside
        # the new_init function, so it has to be put in a new variable
        selfclass = super(AssertInit, cls).__new__(cls, classname, bases, classdict)
        AssertInit._has_real_init[selfclass] = has_real_init
        return selfclass

########### USAGE ############

def test():
    class A(object):
        __metaclass__ = AssertInit
        def __init__(self):
            print 'A init'

    class B(A):
        def __init__(self):
            if random() > 0.5:
                A.__init__(self)
            print 'B init'

    class C(A):
        #__metaclass__ = AssertInit
        pass

    # a separate root class needs to set the __metaclass__ properly
    class G(object):
        __metaclass__ = AssertInit
        def __init__(self):
            print 'G init'

    class D(C, B, G):
        def __init__(self):
            #C.__init__(self)
            B.__init__(self)
            G.__init__(self)
            print 'D init'
    
    # This will raise an error for not calling two base
    # class initializers: A and G.
    # It properly sees that C.__init__ needs not be
    # called and that B.__init__ was called.
    print dir(D())
    #print dir(D)
    

if __name__ == '__main__':
    test()
