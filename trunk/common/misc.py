'''Miscellaneous utilities that don't fit in any other module.'''

from math import ceil as _ceil
from __builtin__ import int as _int
from common.future import *

__author__ = "George Sakkis <gsakkis@rutgers.edu>"
__all__ = ["beautifyOptionHelp", "frange"]

##############################################################################

def frange(*args):
    '''Generalize the builtin range() by allowing float start,stop and step.

    @param args: stop or (start,stop) or (start,stop,step)
    @type args: one,two or three integers.
    '''
    start=0; step=1
    if len(args) == 1: stop = args[0]
    elif len(args) == 2: start,stop = args
    elif len(args) == 3: start,stop,step = args
    else: raise TypeError, "frange() requires 1-3 int arguments"
    for x in stop,start,step:
        if not isinstance(x,int):
            break
    else:
        return range(start,stop,step)
    results = []
    steps = _int(_ceil((stop-start) / float(step)))
    for i in xrange(steps):
        results.append(start)
        start += step
    return results


def beautifyOptionHelp(**kwds):
    '''
    A helper function for for constructing a more informative help message
    for optik.

    @param kwds: Any keyword argument to be passed in C{optik.make_option}.
    @return: A dictionary with the new keyword arguments.
    '''
    help, choices, default = [kwds.get(param) for param in
                              "help", "choices", "default"]
    if choices or default is not None:
        choicesStr = defaultStr = ""
        if choices:
            choicesStr = "options are: %s" % ', '.join(
                                    ["'%s'" % choice for choice in choices])
        if default is not None:
            defaultStr = "default=%s" % default
        if choices and default is not None:
            help = "%s [%s / %s]" % (help,choicesStr,defaultStr)
        else:
            help = "%s [%s]" % (help, choicesStr or defaultStr)
    kwds["help"] = help
    return kwds
