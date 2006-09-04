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
    return _fly(from_, to, schedule, 0, 0, _Infinite, {})[1]


def _fly(from_, to, schedule, day, paidCost, overallCost, cache):
    """Calculates the cheapest route using branch-and-bound and caching of
    partial routes.

    In addition to the arguments of fly, it takes:
        - The index of the starting day (0 for day 1, 1 for day 2, etc.)
        - The cumulative cost paid so far
        - The currently cheapest known overall solution.
        - A cache of precomputed cheapest routes as a dict:
            (from, departure_day) : (minCost,route)

    Returns the optimal solution as (minCost,route), or raises ValueError if
    there is no solution.
    """
    key = from_,day
    cached = cache.get(key)
    if cached is not None:  # cache hit
        return cached
    else:
        if day < len(schedule): # still available flights in schedule
            currentFlights = schedule[day]
            # a stop in the city can be considered as yet another transition
            currentFlights[from_,from_] = 20
            remainingRoute = None
            remainingCost = _Infinite
            # consider flights from the current city only
            # heuristic: sort by ascending price (optional)
            for cost,source,dest in sorted((price,source,dest)
                    for ((source,dest),price) in currentFlights.iteritems()
                    if source == from_):
                newCost = paidCost + cost
                if newCost < overallCost: # bound step of branch and bound
                    if dest != to: # did not reach destination yet
                        try:
                            # branch step of branch and bound
                            restCost,restStops = _fly(dest, to, schedule,
                                        day+1, newCost, overallCost, cache)
                            newCost += restCost
                        except ValueError:
                            # cannot complete the rest of the route; ignore it
                            continue
                    else:
                        restStops = []
                    # update the best partial solution starting from this city
                    # at this day
                    newRemainingCost = newCost-paidCost
                    if newRemainingCost < remainingCost:
                        remainingCost = newRemainingCost
                        remainingRoute = [dest]
                        remainingRoute += restStops
                        # update the best global solution
                        if newCost < overallCost:
                            overallCost = newCost
            # cache and return the best partial solution (if any)
            if remainingRoute is not None:
                return cache.setdefault(key,(remainingCost,remainingRoute))
        raise _NoSolution


_NoSolution = ValueError()

_Infinite = type("Infinite", (object,), { '__cmp__':
                lambda self,other: self is not other and 1 or 0})()

assert 0 < 1e300 < _Infinite == _Infinite > 1e300 > 0


if __name__ == "__main__":
    import fly_test
    fly_test.main(['fly'])
