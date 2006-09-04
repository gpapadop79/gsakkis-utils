'''Date/time string parser.

A (presumably) more robust version of the C{DateTimeFromString} function of
the non standard library C{mx.DateTime.Parser} module.

@todo: Documentation,comments
@todo: doctest
'''

__author__ = "George Sakkis <gsakkis@rutgers.edu>"

import re
from warnings import warn
from time import localtime
if 0:
    from datetime import datetime
    today = datetime.today
else:
    from mx.DateTime import today,DateTime as datetime

__all__ = ["parseDateTime"]

#=============================================================================

def parseDateTime(string, USA=False):
    '''Tries to parse a string as a valid date and/or time.

    It recognizes most common formats:

    @param USA: Disambiguates strings that are valid dates either in
        (month,day,year) or (day,month,year) order (e.g. 05/03/2002). If True,
        the first format is assumed; the default is the second.
    @return: A C{datetime.datetime} instance that represents the parsed string.
    @rtype: datetime.datetime
    @raise ValueError: If the string cannot be interpreted successfully.
    '''
    # create the regexps only the first time this function is called
    if not hasattr(parseDateTime, "regex"):
        item = lambda groupid: r'(?P<%s>\d+|[a-zA-Z]+)' % groupid
        delim = r'[\s\\/,-.]+'
        # negative lookahead/lookbehind assertions on ':' (to prevent mix
        # with time); also negative lookbehind on \w
        dateRegex = "(?<!:|\w)%s%s%s(?:%s%s)?(?!:)" % (item('D1'), delim,
                                                       item('D2'), delim,
                                                       item('D3'))
        timeRegex = r'''(?P<hour>\d{1,2}):                  # hour
                        (?P<minute>\d{1,2})                 # minute
                        (?::(?P<second>\d{1,2}(?:\.\d+)?))? # second
                        (?:\ ?(?P<ampm>[ap]m))?             # 'am', 'pm'
                     '''
        #print r'(?P<date>%s)\s+(?P<time>%s)?' % (dateRegex,timeRegex);
        #import sys; sys.exit()
        # date followed (optionally) by time
        flags = re.VERBOSE | re.IGNORECASE
        parseDateTime.dt_regex = re.compile(
            r'(?P<date>%(dateRegex)s)(?:%(delim)s(?P<time>%(timeRegex)s))?'
            % locals(), flags)
        # or vice versa
        parseDateTime.td_regex = re.compile(
          r'(?P<time>%(timeRegex)s)(?:%(delim)s(?P<date>%(dateRegex)s))?'
          % locals(), flags)
    date = time = None
    match = parseDateTime.dt_regex.match(string.strip()) \
            or parseDateTime.td_regex.search(string.strip())
    if match:
        # parse date
        if match.group("date"):
            triple = [match.group(i) for i in ('D1','D2','D3')]
            if triple[-1] is None:  # 2 date elements given;
                # assume that these are day and month, and add current year
                triple[-1] = str(localtime()[0])
            date = _parseDate(triple, USA)
        else:
            t = today(); date = (t.year,t.month,t.day)
        # parse time
        if match.group("time"):
            hour,minute = [int(match.group(i)) for i in ("hour","minute")]
            ampm = match.group("ampm")
            if ampm is not None and ampm.lower()=='pm':
                hour += 12
            try:    second = float(match.group("second"))
            except: second = 0.0
            if 0<=hour<=23 and 0<=minute<=59 and 0.0<=second<60.0:
                time = (hour,minute,second)
        else: time = ()
    if date is not None and time is not None:
        return datetime(*(date+time))
    else:
        raise ValueError("Unrecognized date/time: %r" % string)


#======== helper functions ===================================================

def _parseDate(triple, USA=False):
    parsed = False
    # 1. try to parse as Year/Month/Day
    year,month,day = (_coerce2Year(triple[0]), _coerce2Month(triple[1]),
                      _coerce2Day(triple[2]))
    if year and month and day:
        parsed = True
    # 2. try to parse as Month/Day/Year or Day/Month/Year
    year2 = _coerce2Year(triple[2])
    month2,day2 = _disambiguateMonthDay(triple[0],triple[1],USA)
    if year2 and month2 and day2:
        if parsed:
            warn("Ambiguous date format: %s (interpreted as %s)" %
                 (triple, datetime(year2,month2,day2).date), stacklevel=3)
        parsed,year,month,day = True,year2,month2,day2
    return parsed and (year,month,day) or None

def _disambiguateMonthDay(first,second,USA=False):
    month,day = _coerce2Month(second), _coerce2Day(first)
    month2,day2 = _coerce2Month(first), _coerce2Day(second)
    if not (day and month) or (day and month and day2 and month2 and USA):
        month,day = month2,day2
    return month,day

def _coerce2Year(string):
    if not hasattr(_coerce2Year, "regex"):
        _coerce2Year.regex = re.compile(r'(\d{4})$|(\d{2})$')
    match = _coerce2Year.regex.match(string)
    if not match:
        return None
    try: return int(match.group(1))
    except TypeError: # 2-digit year
        y = int(match.group(2))
        year = y>30 and 1900+y or 2000+y
        #warnings.warn("Ambiguous year '%d': interpreted as '%d'" % (y,year))
        return year

def _coerce2Month(string):
    if not hasattr(_coerce2Month, "regex"):
        _coerce2Month.regex = re.compile(r'(0?[1-9]|1[012])$|(\w+)$')
    match = _coerce2Month.regex.match(string)
    if not match:
        return None
    try: return int(match.group(1))
    except TypeError:
        return _Month.get(match.group(2).capitalize())

def _coerce2Day(string):
    if not hasattr(_coerce2Day, "regex"):
        _coerce2Day.regex = re.compile(r'(0?[1-9]|[12]\d|3[01])$')
    match = _coerce2Day.regex.match(string)
    return match and int(match.group())

# map months to numbers
_Month = dict(zip(
    ["January", "February", "March", "April", "May", "June",
     "July", "August", "September", "October", "November", "December"],
    range(1,13)))
# ..and vice versa
_Month.update(dict([(i,month) for month,i in _Month.iteritems()]))
# ..and abbreviations (Jan,Feb,...)
_Month.update(dict([(key[:3],i) for key,i in _Month.iteritems()
                    if isinstance(key,str)]))


######################## test converters ########################

if __name__ == "__main__":
    import mx.DateTime
    from common.indent import indent
    dates = [r'01\02\2003',
             "12:32:9",
             "01 02 2003",
             "01-02-2003 / 12:32:9",
             "01 02 2003, 12:32:9",
             "12:32:09 01-02-2003",
             "12:32:19 01 02 2003",
             "5 Mar 3:45pm",
             "3:45pm 5 12 2001",
             "02:7:18.",
             "21:23:39.91",
             "16:15",
             "08:32:40 PM",
             "11:59pm",
             "93/7/18",
             "15.6.2001",
             "3/4/92",
             "1980, November 20",
             "4 Mar 79",
             "July 4",
             "15/08",
             #"22:59:60",
             ]
    if True:
        rows = []
        for string in dates:
            try:
                row = [str(x) for x in
                             string,
                             parseDateTime(string, USA=False),
                             parseDateTime(string, USA=True)]
                rows.append(row)
            except Exception, why:
                print "%s: %s" % (why.__class__.__name__,why)
        labels = ("string","parseDateTime","parseDateTime(US)")
        print indent([labels]+rows, hasHeader=True)
    else:
        rows = []
        for string in dates:
            try:
                row = [str(x) for x in
                             string,
                             mx.DateTime.DateTimeFrom(string),
                             DateTimeFrom(string),
                             DateTimeFrom(string,USA=True)]
                if row[1] != row[2] or row[1] != row[3]:
                    rows.append(row)
            except Exception, why:
                print "%s: %s" % (why.__class__.__name__,why)
        labels = ("string", "mx.DateTime.DateTimeFrom",
                  "parseDateTime", "parseDateTime(US)")
        print indent([labels]+rows, hasHeader=True)
