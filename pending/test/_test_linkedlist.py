#!/usr/bin/env python

if __name__ == '__main__':
    import sys
    def testValidUsage():
        arrayList = ["me","myself","and","I"]
        linkedList = LinkedList(arrayList)

        ################################ accessors ################################
        # indexing,slicing
        for i in xrange(len(arrayList)): assert linkedList[i] == arrayList[i]
        # len
        assert len(linkedList) == len(arrayList)
        # iterator
        assert list(linkedList) == arrayList
        assert "me" in linkedList, "Me" not in linkedList
        # ==, !=
        assert linkedList == linkedList == LinkedList(arrayList) != arrayList
        # str, repr
        assert str(linkedList) == str(arrayList)
        assert eval(repr(linkedList)) == linkedList
        # +
        assert list(linkedList + linkedList) == arrayList + arrayList
        assert id(linkedList + linkedList) != id(linkedList)
        # *
        assert list(3*linkedList) == 3*arrayList
        assert id(3*linkedList) != id(linkedList)
        # count, index
        assert (3*linkedList).count(arrayList[0]) == (3*arrayList).count(arrayList[0])
        assert linkedList.index("and") == arrayList.index("and")

        ################################ mutators ################################
        # assignment
        linkedList[-1] = arrayList[0]; assert linkedList[-1] == linkedList[0]
        # del
        del arrayList[-1], linkedList[-1]; assert list(linkedList) == arrayList
        tmp = LinkedList(["single"]); del tmp[0]; assert list(tmp) == []
        # +=, *=
        linkedList += arrayList; arrayList += arrayList; assert list(linkedList) == arrayList
        linkedList *= 3; arrayList *= 3; assert list(linkedList) == arrayList
        # pop
        assert linkedList.pop(0) == arrayList.pop(0); assert list(linkedList) == arrayList
        assert linkedList.pop() == arrayList.pop(); assert list(linkedList) == arrayList
        # insert
        linkedList.insert(len(arrayList),"w"); arrayList.insert(len(arrayList),"w"); assert list(linkedList) == arrayList
        linkedList.insert(0,"x"); arrayList.insert(0,"x"); assert list(linkedList) == arrayList
        linkedList.insert(1,"y"); arrayList.insert(1,"y"); assert list(linkedList) == arrayList
        linkedList.insert(-1,"z"); arrayList.insert(-1,"z"); assert list(linkedList) == arrayList
        # append, remove, reverse, sort
        linkedList.reverse(); arrayList.reverse(); assert list(linkedList) == arrayList
        linkedList.append("now"); arrayList.append("now"); assert list(linkedList) == arrayList
        linkedList.reverse(); arrayList.reverse(); assert list(linkedList) == arrayList
        linkedList.remove('and'); arrayList.remove('and'); assert list(linkedList) == arrayList
        linkedList.sort(); arrayList.sort(); assert list(linkedList) == arrayList

    def testGetSlicing():
        print >> sys.stderr, "Testing slice get..."
        arrayList = [chr(ord('a') + i) for i in xrange(10)]
        linkedList = LinkedList(arrayList)
        steps = range(-len(linkedList)-1,0) + range(1,len(linkedList)+1)
        starts = stops = [None,0] + steps
        for start in starts:
            for stop in stops:
                for step in steps:
                    try:
                        assert list(linkedList[start:stop:step]) == arrayList[start:stop:step]
                    except Exception, why:
                        print why
                        print start,stop,step
                        print linkedList[start:stop:step]
                        print arrayList[start:stop:step]
                        sys.exit()

    def testSetSlicing(trials=100):
        print >> sys.stderr, "Testing slice set..."
        import random
        orig = [chr(ord('a') + i) for i in xrange(6)]
        steps = range(-len(orig)-1,0) + range(1,len(orig)+1)
        starts = stops = [None,0] + steps
        for start in starts:
            for stop in stops:
                for trial in xrange(trials):
                    arrayList = list(orig)
                    linkedList = LinkedList(orig)
                    while True:
                        begin,end,step = linkedList._validateslice(slice(random.choice(starts),
                                                                         random.choice(stops),
                                                                         random.choice(steps)))
                        if (begin-end)*step < 0: break
                    seq = arrayList[begin:end:step]
                    try:
                        ##print "linkedList[%s:%s] = %s" % (start,stop,seq)
                        linkedList[start:stop] = seq
                        arrayList[start:stop] = seq
                        assert list(linkedList) == arrayList
                    except AssertionError:
                        print "list[%s:%s] = %s" % (start,stop,seq)
                        print "linkedList:", linkedList[start:stop]
                        print "arrayList:", arrayList[start:stop]
                        sys.exit()
                    except Exception, why: print why

    def testInvalidUsage():
        def trycatchblock(*expressions):
            arrayList = ["me","myself","and","I"]
            linkedList = LinkedList(arrayList)
            exceptions = []
            for expr in expressions:
                try: exec expr in locals()
                except Exception, why: exceptions.append(why)
            from indent import indent,wrap_onspace
            print indent([("Expression","Exception class","Message")] + \
                         zip(expressions, map(lambda ex:ex.__class__,exceptions),exceptions),
                         hasHeader=True, separateRows=True,
                         wrapfunc=lambda text:wrap_onspace(str(text),28))

        trycatchblock("linkedList['3']",
                      "linkedList[len(linkedList)]",
                      "linkedList[-len(linkedList)-1]",
                      "linkedList[2:'3']",
                      "linkedList[1:2] = 3",
                      "linkedList[::2] = linkedList",
                      "linkedList[3:4:0]",
                      "linkedList + arrayList",
                      "linkedList.index('not')",
                      "linkedList * '3'",
                      "linkedList.remove('abc')")

    def profiler():
        import profile,pstats
        def benchmark(): #todo
            pass
        filename = 'benchmark.prof'
        profile.run("benchmark()",filename)
        s = pstats.Stats(filename)
        s.sort_stats("cumulative")
        s.print_stats("getitem|setitem|append|pop|insert")



    testValidUsage()
    testInvalidUsage()
    testGetSlicing()
    testSetSlicing()
    #profiler()
