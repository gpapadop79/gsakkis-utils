import sys
__author__ = "George Sakkis"

def fly(from_, to, schedule):
    """fly("Dresden", "Cairo", ...) => ["Berlin", "Athens", "Athens", "Cairo"]

    Calculates the cheapest route starting with "from_" and arriving at "to"
    using the provided schedule.

    Input:

    The schedule is a list of dictionaries. Each dictionary contains the
    schedule for one day of flights. The list is ordered by day i.e. the
    first dictionary contains the schedule for day 1, the second for day 2,
    etc.

    The dictionaries represent a flight schedule as:
    (departure city, arrival city) : flight cost

    Rules:
    - Only one flight per day can be taken
    - Instead of taking a flight, it is possible to wait in the current city,
      which costs 20 EURO per day.

    Output:

    If now route to the destination is possible, ValueError is raised.

    If a route is possible, then it is returned as a list of the cities flown
    to. For each day spend in a city (instead of flying), that city name also
    appears in the list. e.g.
    => ['Berlin', # On day 1, a flight is taken to Berlin
     'Athens',    # On day 2, a flight is taken to Athens
     'Athens,     # On day 3, stay one day in Athens (cost 20 EURO)
     'Dresden]    # On day 4, a flight is taken to Dresden

    Example 1:
    >>> schedule = [
    ... # (from, to) : cost
    ... {('A', 'B') : 100.00, ('A', 'C') : 10.00, ('C', 'B') : 20}, # Day 1
    ... {('A', 'B') : 100.00, ('A', 'C') : 10.00, ('C', 'B') : 20}] # Day 2
    >>> # Calculate the optimal route to fly from A to B. The route should be:
    >>> # Day 1: A => C (cost 20)
    >>> # Day 2: C => B (cost 20)
    >>> fly('A', 'B', schedule)
    ['C', 'B']

    Example 2:
    >>> schedule = [
    ...   # From    # To       # Cost
    ... {('Athens', 'Berlin') : 55.25,   # Day 1 flights
    ...  ('Berlin', 'Athens') : 73.00,
    ...  ('Dresden', 'Athens') : 85.50,
    ...  ('Dresden', 'Berlin') : 12.50},
    ... {('Berlin', 'Athens') : 23.55,   # Day 2 flights
    ...  ('Berlin', 'Cairo') : 125.15,
    ...  ('Berlin', 'Dresden') : 18.25,
    ...  ('Dresden', 'Athens') : 85.50,
    ...  ('Dresden', 'Berlin') : 13.50},
    ... {('Athens', 'Cairo') : 65.55,    # Day 3 flights
    ...  ('Berlin', 'Athens') : 23.55,
    ...  ('Berlin', 'Cairo') : 125.15,
    ...  ('Dresden', 'Athens') : 85.50},
    ... {('Athens', 'Cairo') : 7.25,     # Day 4 flights
    ...  ('Berlin', 'Athens') : 23.55,
    ...  ('Dresden', 'Athens') : 85.50}]

    >>> # Calculate the optimal route to fly from Dresden to Cairo.
    >>> # The route should be:
    >>> # Day 1: Dresden => Berlin (cost 12.50)
    >>> # Day 2: Berlin => Athens (cost 23.55)
    >>> # Day 3: Athens (stay the day: cost of 20)
    >>> # Day 4: Athens => Cairo (cost  7.25)
    >>> # If you think that this route is absurd, let me assure
    >>> # you that I am actually flying it (including the night in
    >>> # Athens) in October
    >>> fly('Dresden', 'Cairo', schedule)
    ['Berlin', 'Athens', 'Athens', 'Cairo']
    >>> # There is now way to get from Cairo to Dresden
    >>> fly('Cairo', 'Dresden', schedule)
    Traceback (most recent call last):
    ...
    ValueError
    """
    if __debug__:
        global missed,prunedList
        missed = 0; prunedList = []
        try:
            return _fly(from_, to, schedule, 0, 0, _Infinite, {})[1]
        finally:
            print >> sys.stderr, "%d calls to _fly" % missed
            #import itertools as it
            #from common import average,standardDeviation
            #for depth,iterGroup in it.groupby(sorted(prunedList), key = lambda x:x[0]):
            #    group = [ratio for depth,ratio in iterGroup]
            #    print >> sys.stderr, "depth %s: %.2f%%" % (depth, average(group))
            #                                                     #standardDeviation(group))
    return _fly(from_, to, schedule, 0, 0, _Infinite, {})[1]

missed = 0
prunedList = []

def _fly(from_, to, schedule, day, paidCost, overallBound, cache):
    """Recursive dynamic programming implementation of fly.

    It takes two extra arguments:
        - The index of the starting day (0 for day 1, 1 for day 2, etc.)
        - A cache of precomputed cheapest routes as a dict:
            (from, to, departure_day) : (minCost,route)

    Returns the optimal solution as (minCost,route), or raises ValueError if
    there is no solution.
    """
    key = from_,to,day
    cached = cache.get(key)
    #if __debug__:
    #    print 2*day*' ', from_, cached is not None and ("(cached: %s)" % cached[0]) or ""
    if cached is not None:  # cache hit
        return cached
    else:
        if __debug__: global missed; missed += 1
        if day < len(schedule): # still available flights in schedule
            currentFlights = schedule[day]
            # a stop in the city can be considered as yet another possible transition
            currentFlights[from_,from_] = 20
            # for every flight today
            _unpruned = 0.0
            remainingRoute = None
            xxx = _Infinite
            # consider flights from the current city only
            # heuristic: sort by ascending price (optional)
            candidates = sorted((price,source,dest) for ((source,dest),price)
                            in currentFlights.iteritems() if source == from_)
            for cost,source,dest in candidates:
            #for ((source,dest),cost) in currentFlights.iteritems():
                currentCost = paidCost + cost
                # bound step
                #if source == from_ and currentCost < overallBound:
                if currentCost < overallBound:
                    if dest != to:
                        try:
                            _unpruned += 1
                            # recursively compute the cheapest route from dest
                            restCost,restStops = _fly(
                                dest, to, schedule, day+1, currentCost,
                                overallBound, cache)
                            currentCost += restCost
                        except ValueError:
                            # cannot complete the rest of the route; ignore it
                            continue
                    else:
                        restStops = []
                    if currentCost-paidCost < xxx:
                        xxx = currentCost-paidCost
                        remainingRoute = [dest]
                        remainingRoute += restStops
                    if currentCost < overallBound:
                        overallBound = currentCost
                        #xxx = currentCost-paidCost
                        #remainingRoute = [dest]
                        #remainingRoute += restStops
            #if __debug__:
            #    prunedList.append((day,100*_unpruned/len(candidates)))
            if remainingRoute is not None:
                return cache.setdefault(key,(xxx,remainingRoute))
        raise ValueError()


_Infinite = type("Infinite", (object,), { '__cmp__':
                lambda self,other: self is not other and 1 or 0})()

assert 0 < 1e300 < _Infinite == _Infinite > 1e300 > 0


if __name__ == "__main__":
    from myfly import timetable
    print fly('Dresden', 'Cairo', timetable)
