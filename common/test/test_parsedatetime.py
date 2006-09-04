#!/usr/bin/env python

import unittest
import datetime
from common.parsedatetime import parseDateTime

__author__ = "George Sakkis <gsakkis@rutgers.edu>"


class ParseDateTimeTestCase(unittest.TestCase):

    def test_parsedate_unambiguous(self):
        table = {
            '93/7/18'           : (1993,7,18),
            '15.6.2001'         : (2001,6,15),
            '6-15-2001'         : (2001,6,15),
            '1980, November 20' : (1980,11,20),
            '4 Mar 79'          : (1979,3,4),
            'July 4'            : (_this_year(),7,4),
            '15/08'             : (_this_year(),8,15),
        }
        for USA in False,True:
            for expr,datetuple in table.iteritems():
                self.assertEqualsDatetime(parseDateTime(expr,USA),
                                          datetime.date(*datetuple))

    def test_parsedate_ambiguous(self):
        exprs = ['01 05 2003', '9-4-92', '11/12']
        dates = [datetime.date(*d_tuple) for d_tuple in
                 (2003,5,1), (1992,4,9), (_this_year(),12,11)]
        for e,d in zip(exprs,dates):
            self.assertEqualsDatetime(parseDateTime(e,USA=False), d)
            self.assertEqualsDatetime(parseDateTime(e,USA=True),
                                      _swap_month_day(d))

    def test_parsetime(self):
        table = {
            '16:15'         : (16,15),
            '12:32:9'       : (12,32,9),
            '02:7:18.'      : (2,7,18),
            '21:23:39.91'   : (21,23,39,910000),
            '08:32:40 PM'   : (20,32,40),
            '11:59pm'       : (23,59),
            '12am'          : (12,),
            '0pm'           : (12,),
            '0am'           : (0,),
        }
        for USA in False,True:
            for expr,t_tuple in table.iteritems():
                self.assertEqualsDatetime(parseDateTime(expr,USA),
                                          datetime.time(*t_tuple))
        # imply current date
        today_date_tuple = datetime.date.today().timetuple()[:3]
        for USA in False,True:
            for expr,t_tuple in table.iteritems():
                self.assertEqualsDatetime(
                    parseDateTime(expr,USA,implyCurrentDate=True),
                    datetime.datetime(*(today_date_tuple+t_tuple)))
        # don't recognize a time just from a single number
        self.assertRaises(ValueError, parseDateTime, "11")
        # 12pm is midnight; should be given as 0am
        self.assertRaises(ValueError, parseDateTime, "12pm")

    def test_parsedatetime_unambiguous(self):
        table = {
            '93_7_18, 2:34'             : (1993,7,18,2,34),
            '9:12:18 15.6.2001'         : (2001,6,15,9,12,18),
            '3:37am / 1980,November 20' : (1980,11,20,3,37),
            '4 Mar 79 20:19:02.45'      : (1979,3,4,20,19,2,450000),
            '6-15-2001 4 pm'            : (2001,6,15,16),
            'July 4 12am'               : (_this_year(),7,4,12),
            '15/08 03:34:21'            : (_this_year(),8,15,3,34,21),
            '3 13 9:05'                 : (_this_year(),3,13,9,5),
        }
        today_date_tuple = datetime.date.today().timetuple()[:3]
        for USA in False,True:
            for expr,dt_tuple in table.iteritems():
                self.assertEqualsDatetime(parseDateTime(expr,USA),
                                          datetime.datetime(*dt_tuple))

    def test_parsedatetime_ambiguous(self):
        exprs = ['07-02-2003 / 5:40',
                 '12:32:09.32, 1 8 2003',
                 '3:45pm 5.11.2001',
                 '6 9 10pm',]
        datetimes = [datetime.datetime(*dt_tuple) for dt_tuple in
                     (2003,2,7,5,40),
                     (2003,8,1,12,32,9,320000),
                     (2001,11,5,15,45),
                     (_this_year(),9,6,22)]
        for e,dt in zip(exprs,datetimes):
            self.assertEqualsDatetime(parseDateTime(e,USA=False), dt)
            self.assertEqualsDatetime(parseDateTime(e,USA=True),
                                      _swap_month_day(dt))

    def assertEqualsDatetime(self,d1,d2):
        self.assertEquals(type(d1), type(d2))
        self.assertEquals(d1,d2)


def _this_year():
    return datetime.date.today().year

def _swap_month_day(date):
    return date.replace(month=date.day, day=date.month)

if __name__ == '__main__':
    unittest.main()
