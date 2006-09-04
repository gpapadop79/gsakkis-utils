#!/usr/bin/env python

'''Script for running the unit test files under one or more directories.

To see the available options, run it from the command line by::
    python test.py --help
'''

import os
import unittest
import itertools as it
try: import optparse
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

            option('-p', '--prefix',
                   help='prefix of the modules to be tested',
                   default='test_'),

            option('-v', '--verbosity',
                   help='unit test verbosity level',
                   type='int',
                   default=1),
            ])
    options,paths = parser.parse_args()
    if not paths:
        paths = ['.']
    testPaths(paths, options.prefix, options.recursive, options.verbosity)


def testPaths(paths, prefix, recursive, verbosity):
    '''Run the unit tests on each path.

    @param paths: An iterable over the files and directories to be tested.
    @param prefix: The prefix of the files to be tested.
    @param recursive: If True, traverse each directory in paths recursively.
    @param verbosity: The test's verbosity level.
    '''
    from os.path import basename, splitext, normpath
    unittest.TextTestRunner(verbosity=verbosity).run(   # suite =
        unittest.TestLoader().loadTestsFromNames(       # module names =
            [splitext(normpath(filepath))[0].replace(os.sep,'.')
             for filepath in it.ifilter(
                lambda path: basename(path).startswith(prefix),
                iterFiles(paths,recursive))]))


def iterFiles(paths, recursive):
    '''Return an iterator over the filenames of the given path(s).

    The returned names are relative to the respective path in paths.

    @param paths: An iterable over paths, or a single path.
    @param recursive: If True, traverse each directory in paths recursively.
    '''
    try:
        from path import path
    except ImportError:
        isdir = os.path.isdir
        iterDir = recursive and _iterFilesRecursive or _iterFiles
    else:
        paths = map(path,paths)
        isdir = path.isdir
        if recursive:
            iterDir = lambda dirpath: dirpath.walkfiles()
        else:
            iterDir = lambda dirpath: iter(dirpath.files())
    return it.chain(*[isdir(p) and iterDir(p) or iter([p]) for p in paths])


def _iterFiles(dirpath):
    '''Return an iterator over the filenames of the given directory.

    The returned names are relative to dirpath.
    '''
    from os.path import join
    return it.ifilter(os.path.isfile, it.imap(lambda name: join(dirpath,name),
                                              os.listdir(dirpath)))

def _iterFilesRecursive(dirpath):
    '''Return an iterator over the filenames of the given directory and its
    subdirectories.

    The returned names are relative to dirpath.
    '''
    join = os.path.join
    for dirpath,dirnames,filenames in os.walk(dirpath):
        for filename in filenames:
            yield join(dirpath,filename)


if __name__ == '__main__':
    main()
