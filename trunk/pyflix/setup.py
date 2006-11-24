#!/usr/bin/env python

#==== imports ==================================================================

import cPickle
from operator import itemgetter
from optparse import OptionParser, make_option

import numpy as N
from path import path

from pyflix import timeCall
from pyflix.records import *
from pyflix.progressbar import ProgressBar, progress

#==== global constants =========================================================

PROBE_SUBDIR = path('probe_set')
TRAINING_SUBDIR = path('training_set')
QUALIFYING_SUBDIR = path('qualifying_set')

SORTED_MOVIE_SUBDIR = path('sorted_by_movie')
SORTED_USER_SUBDIR = path('sorted_by_user')

RECORD_DTYPE = N.dtype('%s,%s' % (MOVIE_ID_TYPECODE,USER_ID_TYPECODE))

#====== main ===================================================================

def main():
    def option(*args, **kwds):
        if 'help' in kwds and 'default' in kwds:
            kwds['help'] += ' [default=%default]'
        return make_option(*args,**kwds)
    parser = OptionParser(
        option_list = [
            option('-i', '--input', default=path('.')/'download',
                     help='Directory containing the Netflix data files'),
            option('-o', '--output', default=path('.')/'bin',
                     help='Directory to store the output binary files'),
            option('--no-movie', action='store_true', default=False,
                   help='Do not generate binary for accessing movie information'),
            option('--no-user', action='store_true', default=False,
                   help='Do not generate binary for accessing user information'),
            option('--no-scrub', action='store_true', default=False,
                   help='Include the training set data that are in the probe set'),
            ##option('-M', '--memory', type='int', default=256,
            ##          help='Rough amount of memory to allocate (in MB)'),
        ])    
    options = parser.parse_args()[0]
    buf = 128 * 1024**2
    buildBinFiles(path(options.input), path(options.output),
               not options.no_movie, not options.no_user, not options.no_scrub,
               read_buf=int(0.75*buf), write_buf=int(0.25*buf))
    
#===============================================================================
    
def buildBinFiles(input_dir, output_dir, do_movies=True, do_users=True, scrub=True,
                  **buffers):
    t_dir, p_dir, q_dir = [output_dir/subdir for subdir in
                           TRAINING_SUBDIR, PROBE_SUBDIR, QUALIFYING_SUBDIR]
    for dir in t_dir, p_dir, q_dir:
        if not dir.exists(): dir.makedirs()
    t_files, p_files = [[dir.joinpath('%d.tmp'%rating) for rating in xrange(1,6)]
                        for dir in t_dir,p_dir]
    # check if all t_files and p_files exist; if not, rebuild them all
    for f in t_files + p_files:
        if not f.exists():
            # 1. split data by rating
            timeCall('  Split files', buildBinTrPrFiles,
                     input_dir/'training_set', t_files,
                     input_dir/'probe.txt', p_files, scrub, **buffers)
            break
    # build qualifying bin file
    q_files = [q_dir/'all.tmp']
    if not q_files[0].exists():
        buildBinQualFile(input_dir/'qualifying.txt', q_files[0])
    for dir, files, isRated in [(t_dir, t_files, True),
                                (p_dir, p_files, True),
                                (q_dir, q_files, False)]:
        # 2. sort each file by movie and/or user
        timeCall('  Sorted files', sortFiles, files, do_movies, do_users)
        # 3. merge them all
        if do_movies:
            recordType = isRated and RatedMovieRecord or UnratedMovieRecord
            timeCall('  Merged movies', mergeSortedFiles, dir, 'movies',
                     SORTED_MOVIE_SUBDIR, 0, recordType, **buffers)
        if do_users:
            recordType = isRated and RatedUserRecord or UnratedUserRecord
            timeCall('  Merged users', mergeSortedFiles, dir, 'users',
                     SORTED_USER_SUBDIR, 1, recordType, **buffers)


def buildBinQualFile(qual_txt, qual_bin, read_buf=-1, write_buf=-1):
    from struct import pack
    print "* Building %s..." % qual_bin
    write = open(qual_bin, 'wb', write_buf).write
    for i,(movie_id, user_id) in enumerate(iterQset(qual_txt,read_buf)):
        write(pack(MOVIE_ID_TYPECODE,movie_id) + pack(USER_ID_TYPECODE,user_id))
    print '  %d qualifying set entries' % (i+1)


def buildBinTrPrFiles(training_dir, training_bin_files,
                      probe_txt, probe_bin_files,
                      scrub=True, read_buf=-1, write_buf=-1):
    '''Split the training set ratings into the training_bin_files, one for each
    rating, and similar for the probe set.
    
    @param scrub: if True, exclude the probe set from the training set.
    '''
    from struct import pack
    print "* Reading %s..." % probe_txt
    probe_set = set(iterPset(probe_txt,read_buf))
    if write_buf > 0:
        # write_buf for each concurrently written file
        write_buf /= (len(training_bin_files) + len(probe_bin_files))
    t_writers, p_writers = [[open(f,'wb',buffering=write_buf).write
                             for f in files]
                            for files in training_bin_files,probe_bin_files]
    num_t_ratings, num_p_ratings = [[0]*len(writers) for writers in t_writers,p_writers]    
    print "* Building rating files..."
    for movie_id, user_id, rating in iterTset(training_dir,read_buf):
        i = rating-1
        entry = pack(MOVIE_ID_TYPECODE,movie_id) + pack(USER_ID_TYPECODE,user_id)
        if (movie_id,user_id) in probe_set:
            p_writers[i](entry); num_p_ratings[i] += 1
            if scrub:
                continue
        t_writers[i](entry); num_t_ratings[i] += 1
    for dataset,num_ratings in [('training set', num_t_ratings),
                                ('probe set', num_p_ratings)]:
        for i,num in enumerate(num_ratings):
            print '  %d %s entries rated %d' % (num,dataset,i+1)


def sortFiles(paths, sort_by_movie=True, sort_by_user=True):
    '''Sort the binary files by movie and/or user'''
    print "* Sorting %s..." % ', '.join(paths)
    def sort_records(path, subdir, field, records=None):
        dir = path.parent/ subdir
        if not dir.exists(): dir.makedirs()
        outfile = dir / path.basename()
        if not outfile.exists():
            if records is None:
                records = N.fromfile(p, RECORD_DTYPE)
            records[records[field].argsort()].tofile(outfile)
        return records
    for p in paths:
        records = None
        if sort_by_movie:
            records = sort_records(p,SORTED_MOVIE_SUBDIR,'f0',records)
        if sort_by_user:
            records = sort_records(p,SORTED_USER_SUBDIR,'f1',records)


def mergeSortedFiles(dir, outfile_prefix, sorted_subdir, sortIndex, recordType,
                     read_buf=-1, write_buf=-1):
    sorted_dir = dir.joinpath(sorted_subdir)
    datfile, idxfile = [dir.joinpath('%s.%s' % (outfile_prefix,ext))
                        for ext in 'dat', 'idx']
    if datfile.exists() and idxfile.exists():
        return
    print "* Merging sorted files from %s ..." % sorted_dir
    entry_size = RECORD_DTYPE.itemsize
    def iter_entries(read):
        # iterate over the (movie_id,user_id) tuples from the reader
        for packed in iter(lambda:read(entry_size), ''):
            yield N.fromstring(packed,RECORD_DTYPE,1)[0]
    # make one entry stream per each sorted-by-rating file
    files = sorted(sorted_dir.files())
    iterators = [iter_entries(open(f,'rb',read_buf/len(files)).read) for f in files]
    key2index = {} # map keys (movie or user IDs) to their index in the fat file
    datfile = open(datfile, 'wb', write_buf)
    progressbar = ProgressBar(0, sum(f.size for f in files)/entry_size, width=70)
    for key,partitioned_values in itermerge(iterators, key=itemgetter(sortIndex),
                                            value=itemgetter(1-sortIndex),
                                            progressbar=progressbar):
        key2index[key] = datfile.tell()
        datfile.write(recordType.fromvalues(key,partitioned_values).tostring())
    cPickle.dump(key2index,open(dir.joinpath('%s.idx' % outfile_prefix), 'wb'))


def itermerge(iterables, key=lambda x:x, value=lambda x:x, progressbar=None): 
    '''Merge one or more sorted iterables.
    
    @param iterables: One or more iterables sorted by key.
    @returns: An iterator that yields pairs (key,value_lists) sorted by key.
        value_lists is a len(iterables) tuple of lists, whose i-th item is the 
        list of values for the items of the i-th iterable having the respective 
        key.        
    '''
    from itertools import chain
    # iterators: a fixed-len list with the i-th element being either an 
    # iterator or None, depending on whether the iterator has been exhausted
    iterators = [None] * len(iterables)
    # cur_entries: maps the indices of the unexhausted iterators to their 
    # current entry
    cur_entries = {}
    for i,iterable in enumerate(iterables):
        iterator = iter(iterable)
        try: cur_entries[i] = iterator.next() 
        except StopIteration: pass 
        else: iterators[i] = iterator
    while cur_entries:
        # get the minimum key
        min_key = min(key(entry) for entry in cur_entries.itervalues())
        # for each iterator, collect the values for the entries with key == min_key
        values = tuple([] for i in iterators)
        for i,iterator in enumerate(iterators):            
            if iterator is not None:
                values_i = values[i]
                for entry in chain([cur_entries.pop(i)], iterator):
                    if key(entry) == min_key:
                        values_i.append(value(entry))
                    else:
                        # finished for this min_x without exhausting the iterator
                        # put back the unused entry 
                        cur_entries[i] = entry
                        break
                else: # this iterator was exhausted
                    iterators[i] = None
        if progressbar is not None:
            progressbar.update(sum(len(v) for v in values))
        yield (min_key, values)
    if progressbar is not None:
        print >> progressbar.out

#======= Row iterators for original text files =================================

def iterMset(path, buffering=1):
    for line in open(path, buffering=buffering):
        movie_id,year,title = line.rstrip().split(',',2)
        year = year!='NULL' and int(year) or None
        yield (int(movie_id), year, title)

def iterTset(dir, buffering=1):
    for f in progress(dir.files(), width=70):
        iterlines = (line.strip() for line in open(f, buffering=buffering))
        movie_id = int(iterlines.next()[:-1])
        for line in iterlines:
            user_id,rating,date = line.split(',',2)
            yield (movie_id, int(user_id), int(rating)) ##,date))

def iterPset(path, buffering=1):
    num_lines = sum(1 for line in open(path,buffering=buffering))
    for line in progress(open(path,buffering=buffering), num_lines, width=70):
        line = line.strip()
        try:
            user_id = int(line)
        except ValueError:
            movie_id = int(line[:-1])
        else:
            yield (movie_id, user_id)

def iterQset(path, buffering=1):
    num_lines = sum(1 for line in open(path,buffering=buffering))
    for line in progress(open(path,buffering=buffering), num_lines, width=70):
        line = line.strip()
        try:
            user_id,date = line.split(',',1)
        except ValueError:
            movie_id = int(line[:-1])
        else:
            yield (movie_id, int(user_id)) ##, date)


if __name__ == '__main__':
    main()
