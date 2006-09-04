#!/usr/bin/env python

import sys,os
import subprocess

_COMMAND = 'ps -s'
_PID_FIELD_INDEX = 0
_NAME_FIELD_INDEX = -1

def findprocs():
    procsByID = {}
    pipe = subprocess.Popen(_COMMAND.split(), stdout=subprocess.PIPE).stdout
    # skip first line
    pipe.next()
    for line in pipe:
        vals = line.split()
        pid = int(vals[_PID_FIELD_INDEX])
        assert pid not in procsByID
        procsByID[pid] = vals[_NAME_FIELD_INDEX]
    # delete the entry for this process
    del procsByID[os.getpid()]
    return procsByID

def killproc(pid,signal="SIGKILL"):
    return not subprocess.call(['kill','-'+signal,str(pid)])


if __name__ == '__main__':
    to_be_killed_substrings = sys.argv[1:]
    for pid,cmd in findprocs().iteritems():
        for substr in to_be_killed_substrings:
            if substr in cmd:
                if killproc(pid):
                    print >> sys.stderr, 'Process %s killed successfully' % pid
                else:
                    print >> sys.stderr, 'Could not kill process %s' % pid
