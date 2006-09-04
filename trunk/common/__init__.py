'''Library of generic utility modules.

For convenience, "from common import *" imports the exported names of
L{common.sequenceutils} and L{common.maputils} (perhaps more will be
added in the future).

@sort: sequenceutils, maputils, typecheck, abstract, parsedatetime, misc,
    future
'''

__author__ = "George Sakkis <gsakkis@rutgers.edu>"

from common.future import *
from common.sequenceutils import *
from common.maputils import *

import sys


def Property(function):
    keys = 'fget', 'fset', 'fdel'
    func_locals = {'doc':function.__doc__}
    def probeFunc(frame, event, arg):
        if event == 'return':
            locals = frame.f_locals
            func_locals.update(dict((k,locals.get(k)) for k in keys))
            sys.settrace(None)
        return probeFunc
    sys.settrace(probeFunc)
    function()
    return property(**func_locals)
