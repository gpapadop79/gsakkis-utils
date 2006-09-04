#!/usr/bin/env python

# todo:
# - join small dirs if bool(preserveStructure)
# - move/copy files
# - cleanup/document

import sys,os
import math
import glob
from optparse import OptionParser, make_option

from common.iterators import any
from common import sorted, sum, flatten

__author__ = "George Sakkis <gsakkis@rutgers.edu>"


def main():
    parser = OptionParser(
        usage = "usage: %prog [options] dir1 ... dirN",
        option_list= [
            make_option("-c", "--capacity",
                        type = "int",
                        default = 736000000,
                        help = "Storage unit capacity (in bytes)"),

            make_option("-r", "--recursive",
                        action = "store_true",
                        help = "Scan each directory recursively"),

            make_option("-i", "--include",
                        action = "append",
                        default = [],
                        help = "Filename pattern of files to be included"
                               " (more than one can be specified)"),

            make_option("-x", "--exclude",
                        action = "append",
                        default = [],
                        help = "Filename pattern of files to be excluded"
                               " (more than one can be specified)"),

            make_option("-p", "--preserveStructure",
                        action = "store_true",
                        help = "Preserve the directory tree hierarchy "
                               "in the partition"),
                     ])

    options,dirs = parser.parse_args()
    if not dirs:
        dirs = ['.']

    fileLists = getFileLists(dirs, options.include, options.exclude,
                             options.recursive, options.preserveStructure)

    getSize = os.path.getsize
    bins = getBins(fileLists, options.capacity, getSize)
    files = flatten(fileLists)
    totalSize = sum(map(getSize,files))
    minBound = int(math.ceil(totalSize / float(options.capacity)))

    print "*** SUMMARY ***"
    print "* %d files (%s)" % (len(files), _sizeAsString(totalSize))
    print "* %s storage unit capacity" % _sizeAsString(options.capacity)
    print "* %d storage units are required at minimum" % minBound
    print "* %d sections were allocated" % len(bins)
    print
    print "* Listing files per unit"
    for i,bin in enumerate(sorted(bins,key=Bin.size,descending=True)):
        print "  - Unit %d (%s / %.2f%%)" % (
                        i, _sizeAsString(bin.size()),
                        100 * bin.size() / float(options.capacity))
        for object in sorted(bin, key=getSize, descending=True):
            print "    %s (%s)" % (object, _sizeAsString(getSize(object)))


def getFileLists(dirs, includeFilters=(), excludeFilters=(), recursive=True,
                 preserveStructure=True):
    files = []
    if not includeFilters:
        includeFilters = ('*',)
    accumulate = preserveStructure and files.append or files.extend
    for dir in dirs:
        accumulate(_getFiles(dir,includeFilters,excludeFilters,
                             recursive,preserveStructure))
    return files


def _getFiles(dir, includeFilters, excludeFilters, recursive, preserveStructure):
    files = []
    kept, thrown = [sum([glob.glob(os.path.join(dir,p)) for p in filters], [])
                    for filters in includeFilters, excludeFilters]
    for fullname in [f for f in kept if f not in thrown]:
        if os.path.isdir(fullname):
            if recursive:
                accumulate = preserveStructure and files.append or files.extend
                accumulate(_getFiles(fullname,includeFilters,excludeFilters,
                                    recursive,preserveStructure))
        else:
            files.append(fullname)
    return files

def getBins(fileLists, capacity, getSize = lambda x:x):
    bins = []
    files = []
    for x in fileLists:
        if isinstance(x,list):
            bins.extend(getBins(x,capacity,getSize))
        else:
            files.append(x)
    return binPacking_bfd(files,capacity,getSize) + bins


def binPacking_bfd(objects, capacity, getSize = lambda x:x):
    return binPacking_bf(sorted(objects,key=getSize,descending=True), capacity,
                         getSize)


def binPacking_bf(objects, capacity, getSize = lambda x:x):
    bins = []
    for object in objects:
        objSize = getSize(object)
        #print >> sys.stderr, "%s (%d)" % (object,objSize)
        newBinSizes = filter(lambda (size,bin): size<=capacity,
                             [(bin.size()+objSize, bin) for bin in bins])
        #print >> sys.stderr, "  newBinSizes:", newBinSizes
        if newBinSizes:
            bestSize,bestBin = max(newBinSizes)
            #print >> sys.stderr, "  bestSize:", bestSize
            bestBin.append(object)
        else:
            #print >> sys.stderr, "  adding new bin"
            bins.append(Bin(capacity,getSize))
            bins[-1].append(object)
    return bins


class Bin:
    def __init__(self, capacity, getSize=lambda x:x):
        self._objects = []
        self._size = 0
        self._capacity = capacity
        self._getSize = getSize

    def __iter__(self):
        return iter(self._objects)

    def size(self):
        return self._size

    def append(self,object):
        newSize = self.size() + self._getSize(object)
        if newSize <= self._capacity:
            self._objects.append(object)
            self._size = newSize
        else:
            raise Bin.Error("Object does not fit in bin")

    class Error(Exception): pass


def _sizeAsString(size, precision=2):
    kb = 1024; mb = kb*kb; gb = mb*kb
    if size < kb:
        return "%d bytes" % size
    else:
        fmt = "%%.%df" % precision
        if size < mb:
            return (fmt + " KB") % (float(size) / kb)
        elif size < gb:
            return (fmt + " MB") % (float(size) / mb)
        else:
            return (fmt + " GB") % (float(size) / gb)


if __name__ == '__main__':
    main()
