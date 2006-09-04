#!/usr/bin/env python

'''Script for running the unit test files under one or more directories.

Each test file is expected to call unittest.main (providing zero or more
optional parameters) from within a guarded region C{if '__name__ == '__main__':}.

To see the available options, run it from the command line by::
    python test.py --help
'''

import sys,os,re
import unittest
try:
    import optparse
except ImportError:
    import optik as optparse

__author__ = 'George Sakkis <gsakkisATrutgersDOTedu>'


def main():
    option = optparse.make_option
    parser = optparse.OptionParser(
        usage = 'usage: %prog [options] filepaths',
        option_list= [
            option('-r', '--recursive',
                   help='search recursively in subdirectories for test '
                        'files [on by default]',
                   action='store_true',
                   default=True),

            option('-l', '--local',
                   help='do not search recursively for test files',
                   action='store_false',
                   dest='recursive'),

            option('-p', '--pattern',
                   help='regular expression for the modules to be tested',
                   default='test_.+'),
            ])
    options,paths = parser.parse_args()
    if not paths: paths = ['.']
    del sys.argv[1:] # need this so that unittest.main does not use them
    testPaths(paths, options.pattern, options.recursive)


def testPaths(paths, basenamePattern='.+', recursive=False):
    '''Run the unit tests on each path.

    @param paths: An iterable over file paths.
    @param basenamePattern: The name pattern of the python files to be tested.
    @param recursive: If True, traverse each directory in paths recursively.
    '''
    matcher = re.compile(r'^%s\.py$' % basenamePattern).match
    for path in paths:
        _testPath(path, matcher, recursive)


def _testPath(path, matcher, recursive):
    '''Run the unit test of one or more files.

    @param path: A path of a file or a directory. If it is a file, the
        respective module is unit tested. If it is a directory, the files
        under it that match the matcher are tested.
    @param matcher: A regular expression to be matched against the modules
        to be unit tested.
    @param recursive: If True, traverse each directory under path recursively.
    '''
    try: # if path is a directory
        children = os.listdir(path)
        dir = path
    except OSError: # it's not a dir; split it
        dir,name = os.path.split(path)
        children = [name]
    # maps module names to filenames
    modulesDict = {}
    for child in children:
        fullpath = os.path.normpath(os.path.join(dir,child))
        modulename = os.path.splitext(fullpath)[0].replace(os.sep,'.')
        if os.path.isfile(fullpath) and matcher(child):
            modulesDict[modulename] = fullpath
        elif recursive and os.path.isdir(fullpath):
            _testPath(fullpath,matcher,recursive)
    # XXX: ugly kludge follows:
    # Can it be done without messing with sys.modules['__main__'] ?
    this_module = sys.modules[__name__]
    for modulename,file in modulesDict.iteritems():
        sys.modules['__main__'] = _importModule(modulename)
        try:
            print 'Testing %s' % file
            execfile(file, {'__name__': '__main__'})
        except SystemExit: pass
        # XXX: don't know why, but this is necessary
        sys.modules['__main__'] = this_module


def _importModule(name):
    '''Return the module with the given name.

    Contrary to __import__('A.B.module'), _importModule('A.B.m') imports m
    instead of the top level package A.
    '''
    module = __import__(name)
    for part in name.split('.')[1:]:
        module = getattr(module, part)
    return module


if __name__ == '__main__':
    main()
