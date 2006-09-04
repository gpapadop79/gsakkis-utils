#!/usr/bin/env python

'''Robust date/time string parser.'''

import re, datetime, warnings

__author__ = "George Sakkis <gsakkis@rutgers.edu>"
__all__ = ["parseDateTime"]

#=============================================================================

def _20thcenturyHeuristic(year):
    if year >= 1000: return year
    if year >= 10:   return 1900+year
    return None

def parseDateTime(string, USA=False, implyCurrentDate=False,
                  yearHeuristic=_20thcenturyHeuristic):
    '''Tries to parse a string as a valid date and/or time.

    It recognizes most common (and less common) date and time formats.

    Examples:
        >>> # doctest was run succesfully on...
        >>> str(datetime.date.today())
        '2005-05-16'
        >>> str(parseDateTime('21:23:39.91'))
        '21:23:39.910000'
        >>> str(parseDateTime('16:15'))
        '16:15:00'
        >>> str(parseDateTime('10am'))
        '10:00:00'
        >>> str(parseDateTime('2:7:18.'))
        '02:07:18'
        >>> str(parseDateTime('08:32:40 PM'))
        '20:32:40'
        >>> str(parseDateTime('11:59pm'))
        '23:59:00'
        >>> str(parseDateTime('12:32:9'))
        '12:32:09'
        >>> str(parseDateTime('12:32:9', implyCurrentDate=True))
        '2005-05-16 12:32:09'
        >>> str(parseDateTime('93/7/18'))
        '1993-07-18'
        >>> str(parseDateTime('15.6.2001'))
        '2001-06-15'
        >>> str(parseDateTime('6.15.2001'))
        '2001-06-15'
        >>> str(parseDateTime('1980, November 20'))
        '1980-11-20'
        >>> str(parseDateTime('4 Mar 79'))
        '1979-03-04'
        >>> str(parseDateTime('July 4'))
        '2005-07-04'
        >>> str(parseDateTime('15/08'))
        '2005-08-15'
        >>> str(parseDateTime('5 Mar 3:45pm'))
        '2005-03-05 15:45:00'
        >>> str(parseDateTime('01 02 2003'))
        '2003-02-01'
        >>> str(parseDateTime('01 02 2003', USA=True))
        '2003-01-02'
        >>> str(parseDateTime('3/4/92'))
        '1992-04-03'
        >>> str(parseDateTime('3/4/92', USA=True))
        '1992-03-04'
        >>> str(parseDateTime('12:32:09 1-2-2003'))
        '2003-02-01 12:32:09'
        >>> str(parseDateTime('12:32:09 1-2-2003', USA=True))
        '2003-01-02 12:32:09'
        >>> str(parseDateTime('3:45pm 5 12 2001'))
        '2001-12-05 15:45:00'
        >>> str(parseDateTime('3:45pm 5 12 2001', USA=True))
        '2001-05-12 15:45:00'

    @param USA: Disambiguates strings that are valid dates in both (month,
        day, year) and (day, month, year) order (e.g. 05/03/2002). If True,
        the first format is assumed.
    @param implyCurrentDate: If True and the date is not given, the current
        date is implied.
    @param yearHeuristic: If not None, a callable f(year) that transforms the
        value of the given year. The default heuristic transforms 2-digit
        years to 4-digit years assuming they are in the 20th century::
            lambda year: (year >= 100 and year
                          or year >= 10 and 1900 + year
                          or None)
        The heuristic should return None if the year is not considered valid.
        If yearHeuristic is None, no year transformation takes place.
    @return:
        - C{datetime.date} if only the date is recognized.
        - C{datetime.time} if only the time is recognized and implyCurrentDate
            is False.
        - C{datetime.datetime} if both date and time are recognized.
    @raise ValueError: If the string cannot be parsed successfully.
    '''
    # create the regexps only the first time this function is called
    if not hasattr(parseDateTime, "regex"):
        flags = re.VERBOSE | re.IGNORECASE
        delim = r'[\s\\/,-._]+'
        item = lambda groupid: r'(?P<%s>\d+|[a-zA-Z]+)' % groupid
        # negative lookahead/lookbehind assertions on ':' (to prevent mix
        # with time); also negative lookbehind on \w
        dateRegex = "(?<!:|\w)%s%s%s(?:%s%s)?(?!:)" % (item('D1'), delim,
                                                       item('D2'), delim,
                                                       item('D3'))
        timeRegex = r'''(?P<hour>\d{1,2})               # hour
                        (?::(?P<minute>\d{1,2})         # minute
                            (?::(?P<second>\d{1,2})     # second
                                (?:\.(?P<msec>\d+)?)?   # microsec
                            )?                          # (close second)
                        )?                              # (close minute)
                        (?:\ ?(?P<ampm>[ap]m))?         # 'am'/'pm'
                     '''
        # date followed (optionally) by time
        parseDateTime.dt_regex = re.compile(
            r'^(?P<date>%(dateRegex)s)(?:%(delim)s(?P<time>%(timeRegex)s))?$'
            % locals(), flags)
        # or vice versa
        parseDateTime.td_regex = re.compile(
          r'^(?P<time>%(timeRegex)s)(?:%(delim)s(?P<date>%(dateRegex)s))?$'
          % locals(), flags)
    date = time = None
    match = parseDateTime.dt_regex.match(string.strip()) \
            or parseDateTime.td_regex.match(string.strip())
    if match:
        # parse date
        if match.group("date"):
            triple = [match.group(i) for i in ('D1','D2','D3')]
            if triple[-1] is None:  # 2 date elements given;
                # assume that these are day and month, and add current year
                triple[-1] = str(_thisyear())
            if yearHeuristic is None:
                yearHeuristic = lambda year: year
            date = _parseDate(triple, USA, yearHeuristic)
        elif implyCurrentDate:
            t = _today()
            date = (t.year,t.month,t.day)
        # parse time
        if match.group("time"):
            hour,minute,second,microsec,ampm = [
                match.group(field) for field in "hour", "minute", "second",
                                                "msec", "ampm"]
            hour = int(hour)
            # refuse to recognize a time just from a single int (i.e. without
            # minutes and/or 'am','pm' specification)
            if minute is not None or ampm is not None:
                minute = minute is not None and int(minute) or 0
                second = second is not None and int(second) or 0
                if microsec is not None:
                    # convert microsec from string to int in microseconds
                    # e.g. '57' -> 570000
                    microsec = int(("%-6d" % int(microsec)).replace(' ','0'))
                else:
                    microsec = 0
                if ampm is not None and ampm.lower()=='pm':
                    hour += 12
                time = (hour,minute,second,microsec)
        if date is not None:
            if time is not None:
                return datetime.datetime(*(date+time))
            else:
                return datetime.date(*date)
        elif time is not None:
            return datetime.time(*time)
    raise ValueError("Unrecognized date/time: %r" % string)


#======== helper functions ===================================================

def _today():
    return datetime.date.today()

def _thisyear():
    return _today().year

def _parseDate(triple, USA=False, yearHeuristic=None):
    parsed = False
    # 1. try to parse as Year/Month/Day
    year,month,day = (_coerce2Year(triple[0], yearHeuristic),
                      _coerce2Month(triple[1]), _coerce2Day(triple[2]))
    if year and month and day:
        parsed = True
    # 2. try to parse as Month/Day/Year or Day/Month/Year
    year2 = _coerce2Year(triple[2], yearHeuristic)
    month2,day2 = _disambiguateMonthDay(triple[0],triple[1],USA)
    if year2 and month2 and day2:
        if parsed: warnings.warn(
            "Ambiguous date format: %s (interpreted as %s)" %
            (triple, datetime.date(year2,month2,day2)), stacklevel=3)
        parsed,year,month,day = True,year2,month2,day2
    return parsed and (year,month,day) or None

def _disambiguateMonthDay(first,second,USA=False):
    month,day = _coerce2Month(second), _coerce2Day(first)
    month2,day2 = _coerce2Month(first), _coerce2Day(second)
    if not (day and month) or (day and month and day2 and month2 and USA):
        month,day = month2,day2
    return month,day

def _coerce2Year(string, heuristic=None):
    try:
        y = int(string)
        if heuristic is not None:
            y = heuristic(y)
        return y
    except ValueError:
        return None

def _coerce2Month(string):
    try:
        m = int(string)
        if 1 <= m <= 12:
            return m
        return None
    except ValueError:
        if not hasattr(_coerce2Month, 'months_table'):
            # map months to numbers
            months_table = dict(zip(
                """January February March April May June July August September
                   October November December""".split(), range(1,13)))
            # ..and vice versa
            months_table.update(dict([(i,month) for month,i in
                                      months_table.iteritems()]))
            # ..and abbreviations (Jan,Feb,...)
            months_table.update(dict(
                [(key[:3],i) for key,i in months_table.iteritems()
                 if isinstance(key,str)]))
            _coerce2Month.months_table = months_table
        return _coerce2Month.months_table.get(string.capitalize())

def _coerce2Day(string):
    try:
        d = int(string)
        if 1<= d <= 31: return d
    except ValueError: pass
    return None


if __name__ == "__main__":
    import doctest; doctest.testmod()
