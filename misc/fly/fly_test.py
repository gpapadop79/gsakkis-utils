#!/usr/bin/env python

"""
Used to test and time solutions to this contest.

If you have filled in the stub module "fly.py" then this
is a reasonable way to test it:

python fly_test.py --trials=5 fly

Note that XML-RPC calls are mode to verify your solution so it may
be quite slow for large trials.
"""

import random
from pprint import pprint, pformat
import logging
from logging import DEBUG, INFO, ERROR
import copy

def generate_schedule():
    """generate_schedule() => \
            [{('Athens', 'Berlin') : 55.25,   # Day 1
              ('Berlin', 'Athens') : 73.00,
              ('Dresden', 'Athens') : 85.50,
              ('Dresden', 'Berlin') : 12.50},
             {('Berlin', 'Athens') : 23.55,   # Day 2
              ('Berlin', 'Cairo') : 125.15,
              ('Berlin', 'Dresden') : 18.25,
              ('Dresden', 'Athens') : 85.50,
              ('Dresden', 'Berlin') : 13.50},
             {('Athens', 'Cairo') : 65.55,    # Day 3
              ('Berlin', 'Athens') : 23.55,
              ('Berlin', 'Cairo') : 125.15,
              ('Dresden', 'Athens') : 85.50},
             {('Athens', 'Cairo') : 7.25,     # Day 4
              ('Berlin', 'Athens') : 23.55,
              ('Dresden', 'Athens') : 85.50}]

    Generates a random flight schedule.
    """
    cities = 'Athens Berlin Cairo Dresden London Madrid Moscow Oslo Paris ' \
             'Praque Rome Stockholm Valletta Warsaw'.split(' ')
    schedule = []
    for day in range(random.randint(2, 30)):
        day_schedule = {}
        schedule.append(day_schedule)
        for from_ in random.sample(
                        cities, random.randint(len(cities) / 2, len(cities))):
            for to in random.sample(cities, random.randint(1, len(cities))):
                if from_ == to:
                    continue

                day_schedule[(from_, to)] = random.randint(500, 15000) / 100.0
    return schedule

def pick_cities(schedule):
    """pick_cities(schedule) => 'Paris', 'London'

    Picks two cities randomly from the schedule to ask as
    the start and destiation.
    """

    day = random.choice(schedule)
    from_ = random.choice(day.keys())[0]

    day = random.choice(schedule)
    to = random.choice([f[1] for f in day.keys() if f[1] != from_])

    return from_, to

def calculate_cost(from_, to_, route, schedule):
    """calculate_cost('Paris', 'London', ['Berlin', 'London'], schedule) => 63.2

    Calculates the cost of taking a particular route from the starting city to
    the ending city. Raises a ValueError if the route doesn't end in the ending
    city or if the route takes a flight which doesn't exist.
    """
    cost = 0
    next = None

    for i, next in enumerate(route):
        if from_ == next: # Staying in the same place costs 20
            cost += 20
        else:
            try:
                cost = cost + schedule[i][(from_, next)]
            except (IndexError, KeyError):
                raise ValueError

            from_ = next

    if to_ != next:
        raise ValueError

    return cost

def test(module, trials, validate=True):
    """Prints out timings for a perticular module"""

    from timeit import default_timer

    level = logging.getLogger().getEffectiveLevel( )

    total = 0
    print 'Testing "%s"...' % (module.__author__),
    for i in range(trials):
        schedule = generate_schedule()
        from_, to = pick_cities(schedule)

        if level <= DEBUG:
            logging.log(DEBUG, "schedule:\n%s", pformat(schedule))
        logging.log(INFO, 'Routing problem: %s => %s', from_, to)

        if validate:
            import oracle
            try:
                oracle_route = oracle.fly(from_, to, schedule)
            except ValueError:
                possible = False
            else:
                possible = True
                oracle_cost = calculate_cost(
                    from_, to, oracle_route, schedule)

                logging.log(
                    INFO, 'Oracle route: %r (cost: %r)', oracle_route, oracle_cost)

        # todo: deepcopy schedule before passing it to module.fly
        schedule_copy = copy.deepcopy(schedule)
        time1 = default_timer()
        try:
            route = module.fly(from_, to, schedule_copy)
        except ValueError:
            time2 = default_timer()
            if validate and possible:
                logging.error('incorrect ValueError on test %d', i)
                break
            else:
                subtotal = time2 - time1
                total = total + subtotal
        except Exception, e:
            logging.error('exception raised on test %d [%s]', i, e)
            break
        else:
            time2 = default_timer()
            subtotal = time2 - time1
            logging.log(INFO, 'Test Route:  %s (time: %s)', route, subtotal)

            total = total + subtotal
            if validate and not possible:
                logging.error(
                    'generated impossible route [%r] on test %d', route, i)
                break

            try:
                cost = calculate_cost(from_, to, route, schedule)
            except ValueError:
                if validate:
                    logging.error(
                        'generated invalid route [%r] on test %d', route, i)
                    break
            else:
                if validate and cost > oracle_cost + 0.01:
                    logging.error(
                        'generated sub-optimal route [%r, %r] on test %d',
                        route, cost, i)
                    break
                elif validate and cost + 0.01 < oracle_cost:
                    logging.critical(
                        "uh oh...my implementation isn't very good")


    else:
        print '%f seconds' % total

import sys

def main(modules=[]):
    from optparse import OptionParser
    parser = OptionParser(
        usage="usage: %prog [options] module1 module2 ...")

    parser.add_option(
        '-s', '--seed',
        action="store",
        type="int",
        dest="seed",
        metavar="SEED",
        help="sets random.seed to this value for repeatable tests")

    parser.add_option(
        "-l", "--level",
        choices=["DEBUG", "INFO", "ERROR"],
        dest="logging_level",
        action="store",
        default="ERROR",
        metavar="LEVEL",
        help="print diagnostic information")

    parser.add_option(
        "-f", "--log-file",
        type="string", dest="logging_file",
        action="store",
        metavar="FILE",
        help="log to specified file (default is stderr)")

    parser.add_option(
        '-t', '--trials',
        action="store",
        type="int",
        dest="trials",
        default=50,
        metavar="COUNT",
        help="sets the number of test trials to execute")

    parser.add_option(
        '-v', '--validate',
        action="store_true",
        help="check the correctness of the tested solution")

    options, arguments = parser.parse_args()

    arguments = modules + arguments
    if options.logging_file:
        kwargs = dict(filename=options.logging_file, filemode='w')
    else:
        kwargs = {}
    logging.basicConfig(level={
                            "DEBUG" : DEBUG,
                            "INFO" : INFO,
                            "ERROR" : ERROR
                        }[options.logging_level],
                        format='%(message)s',
                        **kwargs)

    if len(arguments) == 0:
        parser.error(
            "at least one module must be specified")
    else:
        try:
            for modname in arguments:
                if modname.endswith('.py'):
                    modname = modname[:-3]
                module = __import__(modname)

                random.seed(options.seed)
                test(module, options.trials, options.validate)
        finally:
            logging.shutdown()

if __name__ == "__main__":
    main()
