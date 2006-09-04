timetable = [
    # From    # To       # Cost
    {('Athens', 'Berlin') : 55.25,   # Day 1 flights
     ('Berlin', 'Athens') : 73.00,
     ('Dresden', 'Athens') : 85.50,
     ('Dresden', 'Berlin') : 12.50},
    {('Berlin', 'Athens') : 23.55,   # Day 2 flights
     ('Berlin', 'Cairo') : 125.15,
     ('Berlin', 'Dresden') : 18.25,
     ('Dresden', 'Athens') : 85.50,
     ('Dresden', 'Berlin') : 13.50},
    {('Athens', 'Cairo') : 65.55,    # Day 3 flights
     ('Berlin', 'Athens') : 23.55,
     ('Berlin', 'Cairo') : 125.15,
     ('Dresden', 'Athens') : 85.50},
    {('Athens', 'Cairo') : 7.25,     # Day 4 flights
     ('Berlin', 'Athens') : 23.55,
     ('Dresden', 'Athens') : 85.50}
    ]

     # Calculate the optimal route to fly from Dresden to Cairo.
     # The route should be:
     # Day 1: Dresden => Berlin (cost 12.50)
     # Day 2: Berlin => Athens (cost 23.55)
     # Day 3: Athens (stay the day: fixed cost of 20)
     # Day 4: Athens => Cairo (cost  7.25)



def fly(from_, to, schedule):
    #cities = set(sum([[s,d] for day in schedule for s,d in day], []))
    #for day in timetable:
    #    for city in cities:
    #        day[city,city] = 20.0
    return _fly(from_, to, schedule, 0, {})[1]

def _fly(from_, to, schedule, day, cache):
    key = from_,to,day
    cached = cache.get(key)
    if cached is not None:
        return cached
    if from_ == to:
        solution = 0.0,[]
    else:
        solution = min(iterSchedules(from_, to, schedule, day, cache))
    return cache.setdefault(key, solution)


def iterSchedules(from_, to, schedule, day, cache):
    if day < len(schedule):
        currentFlights = schedule[day]
        currentFlights[from_,from_] = 20
        for ((source,dest),price) in currentFlights.iteritems():
            if source == from_:
                try:
                    restPrice,restStops = _fly(dest, to, schedule, day+1, cache)
                    yield price+restPrice, [dest]+restStops
                except ValueError:
                    pass
        del currentFlights[from_,from_]


if __name__ == '__main__':
    print fly('Dresden', 'Cairo', timetable)
    print fly('Cairo', 'Dresden', timetable)
    if 0:
        import timeit
        from random import sample
        cities = "Athens Berlin Dresden Cairo".split()
        for i in xrange(20):
            a,b = sample(cities,2)
            assert fly2(a,b,timetable) == fly3(a,b,timetable)

            times = [min(timeit.Timer("%s(%r,%r,timetable)" % (f,a,b),
                             "from fly import timetable,%s" % f).repeat(3,10000))
                     for f in "fly2","fly3"]
            print a,b,times[0]/times[1]
    #print count
    #print fly2('Dresden', 'Cairo', timetable)
    #print count2,hits,missed


#def fly(departFrom, arriveTo, timetable):
#    try: return min(generateFlights(departFrom, arriveTo, timetable))
#    except: return None
#
#count = 0
#def generateFlights(departFrom, arriveTo, timetable, _startday=0):
#    #print ' '*_startday*4, departFrom, arriveTo, _startday
#    global count; count += 1;
#    #print "#", count, depth, departFrom
#    if departFrom == arriveTo:
#        yield (0.0, [arriveTo])
#    elif timetable:
#        candidates = timetable.pop(0)
#        candidates[departFrom,departFrom] = STOP_COST
#        for ((source,dest),price) in candidates.iteritems():
#            if source == departFrom:
#                firstStop = [source]
#                for restPrice,restStops in generateFlights(dest,arriveTo,timetable,_startday+1):
#                    yield (price+restPrice, firstStop+restStops)
#        del candidates[departFrom,departFrom]
#        timetable.insert(0, candidates)


#def fly2(departFrom, arriveTo, timetable):
#    minPrice,stops = _fly2(departFrom, arriveTo, timetable, 0)
#    #if minPrice is _Largest:
#    #    raise ValueError
#    return minPrice,stops
#
#def _fly2(departFrom, arriveTo, timetable, _startday=0):
#    #global count2,hits,missed
#    #count2 += 1
#    cached = cache.get((departFrom,arriveTo,_startday))
#    #print ' '*_startday*4, departFrom, arriveTo, _startday, cached and "hit"
#    if cached is not None:
#        #hits +=1
#        return cached
#    else:
#        #missed +=1
#        #print "#", count, depth, departFrom
#        minPrice,bestTrip = _Largest, None
#        if departFrom == arriveTo:
#            minPrice,bestTrip = 0.0,[arriveTo]
#        elif timetable:
#            candidates = timetable.pop(0)
#            candidates[departFrom,departFrom] = STOP_COST
#            for ((source,dest),price) in candidates.iteritems():
#                if source == departFrom:
#                    restPrice,restStops = _fly2(dest, arriveTo, timetable,
#                                               _startday+1)
#                    try:
#                        if price+restPrice < minPrice:
#                            minPrice = price+restPrice
#                            bestTrip = [source] + restStops
#                    except TypeError:
#                        pass
#            del candidates[departFrom,departFrom]
#            timetable.insert(0, candidates)
#        return cache.setdefault((departFrom,arriveTo,_startday),
#                                    (minPrice,bestTrip))
#
