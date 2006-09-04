#!/usr/bin/env python

#todo: API, update

import sys
import re
from warnings import warn
from urllib import urlopen
from urlparse import urljoin
from BeautifulSoup import BeautifulSoup
from xml.dom.ext import PrettyPrint

from pending.xmlify import xmlify


class RealSynthetic(object):

    def __init__(self, url='http://www.synthetic.org/play.html'):
        self.playlists = []
        page = BeautifulSoup(urlopen(url))
        for link in page.fetch('a', {'href':re.compile(r'play/rsa\d+\.htm')}):
            iterMonthLists = iterMonthPlayLists(urljoin(url, link['href']))
            try: self.playlists.extend(iterMonthLists)
            except ValueError: warn('unparsed link: %s' % link)

    def __iter__(self):
        return iter(self.playlists)


class PlayList(object):
    def __init__(self, selections, date):
        self.date = date
        self.selections = [self.Entry(*selection) for selection in selections]

    def __repr__(self):
        return repr(self.__dict__)

    class Entry(object):
        def __init__(self, artist, title):
            self.artist,self.title = artist,title


class Date(object):
    def __init__(self, year, month, day):
        self.year,self.month,self.day = year,month, day

def iterMonthPlayLists(url):
    page = BeautifulSoup(urlopen(url))
    wordRE = re.compile(r'\w+')
    for table in page.fetch('table'):
        rows = iter(table.fetch('tr'))
        # first row: the date
        month,day,year = map(int,''.join(rows.next().fetchText(wordRE)).split('/'))
        # second row: title,artist labels; ignore it
        rows.next()
        # remaining rows : title,artist data
        selections = [[''.join(col.fetchText(wordRE)).strip()
                       for col in row.fetch('td')] for row in rows]
        yield PlayList(selections, Date(year,month,day))


if __name__ == '__main__':
    rsa = RealSynthetic(*sys.argv[1:])
    PrettyPrint(xmlify(rsa, 'RealSyntheticAudio', writetype=False,
                       writemodule=False, deepcopy=True))
