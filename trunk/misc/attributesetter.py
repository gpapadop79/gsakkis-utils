#__author__ = "George Sakkis <gsakkis@rutgers.edu>"
#
#
#def autoinit(exclude=(), underscores=1):
#    '''
#
#    @param exclude: A sequence of the names to be excluded from being set
#        the attributes set the caller's formal arguments (required and optional), plus
#        * a tuple for the caller's positional argument list (*args), if any, plus
#        * the named arguments the caller may have (**kwds).
#    @param underscores: Number of underscores to prepend to each attribute.
#    '''
#    from inspect import currentframe, getargvalues, stack
#    # get caller's frame
#    argNames, posname, kwdsname, locals = getargvalues(currentframe(1))
#    # get the object to be assigned from locals
#    try: assignedobject = locals.pop(objectname)
#    except KeyError:
#        raise KeyError("'%s' not in locals()" % objectname)
#    # if there are named arguments, add them to a fresh copy of locals
#    if kwdsname:
#        locals = dict(locals)
#        for attr,value in locals[kwdsname].iteritems():
#            if attr in locals:
#                fname = stack()[1][3]
#                raise TypeError("%s() got multiple values for "
#                                "keyword argument '%s'" % (fname,attr))
#            locals[attr] = value
#    if not attrNames:
#        attrNames = argNames
#        # store caller's positional arguments as a single list attribute
#        if posname: attrNames.append(posname)
#        # store caller's named arguments as separate attributes
#        if kwdsname: attrNames += locals[kwdsname].keys()
#        # don't set objectname as attribute !
#        try: attrNames.remove(objectname)
#        except ValueError: pass
#    attrDict = {}
#    for name in attrNames:
#        attrDict[name] = locals[name]
#    for attr,value in attrDict.iteritems():
#        attr = "%s%s" % (underscores*'_' , attr)
#        setattr(assignedobject,attr,value)
#
#
#    #class Test(object):
#    #    def __init__(self,foo,bar,baz,boom=1,bang=2,*pos,**kwds):
#    #        x=2
#    #        attributeSetter(attrNames=None, privacyLevel=2)
#    #        y=2
#    #
#    #class Test2(Test):
#    #    def __init__(self,foo,bar,baz,boom=1,bang=2,*pos,**kwds):
#    #        super(Test2,self).__init__(foo,bar,baz,boom,bang)
#    #
#    #
#    #print Test2('a','b','c',12,13,14,fin="me",gon="you",ps=19).__dict__
#    #
#    #class SetAt(object):
#    #    def __init__(self, x):
#    #        self.x =x
#    #    def __setattr__(self,name,value):
#    #        if name == 'x': print "changing x"
#    #        super(SetAt,self).__setattr__(name,value)
#    #    def __hash__(self): return hash(self.x)
#    #
#    #
#    #
#    #o = SetAt([1,2,3]); print o.x
#    #z=range(10)
#    #o.x=z
#    #z=[3]#z.append(1)
#    #print o.x
#    #a = SetAt(1)
#    #d= {a:1, SetAt(2):2}
#    #print a in d,d
#    #a.x = 3
#    #print a in d,d
