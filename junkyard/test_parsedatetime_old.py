#!/usr/bin/env python

if __name__ == "__main__":
    import mx.DateTime
    from common.indent import indent
    datetimes = [
        "12:32:9",
        "5 Mar 3:45pm",
        "02:7:18.",
        "21:23:39.91",
        "16:15",
        "08:32:40 PM",
        "11:59pm",
        "93/7/18",
        "15.6.2001",
        "1980, November 20",
        "4 Mar 79",
        "July 4",
        "15/08",
        "01 02 2003",
        "01_02_2003",
        "3/4/92",
        "01-02-2003 / 12:32:9",
        "01 02 2003, 12:32:9",
        "12:32:09 01-02-2003",
        "12:32:09, 01 02 2003",
        "3:45pm 5 12 2001",
    ]

    import doctest; doctest.testmod()
    if 0:
        for string in datetimes:
            exprs = ["str(parseDateTime(%r%s))" % (string,restexpr)
                     for restexpr in "", ", USA=True"]
            vals = [repr(eval(expr)) for expr in exprs]
            print ">>>", exprs[0]
            print vals[0]
            if vals[0] != vals[1]:
                print ">>>", exprs[1]
                print vals[1]
    if 0:
        rows = []
        for string in datetimes:
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
    if 0:
        rows = []
        for string in datetimes:
            try:
                row = [str(x) for x in
                             string,
                             mx.DateTime.DateTimeFrom(string),
                             parseDateTime(string),
                             parseDateTime(string,USA=True)]
                if row[1] != row[2] or row[1] != row[3]:
                    rows.append(row)
            except Exception, why:
                print "%s: %s" % (why.__class__.__name__,why)
        labels = ("string", "mx.DateTime.DateTimeFrom",
                  "parseDateTime", "parseDateTime(US)")
        print indent([labels]+rows, hasHeader=True)
