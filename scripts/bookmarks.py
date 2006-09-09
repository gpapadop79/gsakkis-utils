#!/usr/bin/env python

import BeautifulSoup as bs
if bs.__version__ < '3':
    raise RuntimeError('BeautifulSoup 3.0 required')


def parseBookmarks(path):
    '''Parse a Firefox bookmarks html file into xml format, preserving the
    hierarchical structure of the original.
    
    @rtype: BeautifulStoneSoup
    '''
    writer = bs.BeautifulStoneSoup()
    # helper Tag factory
    def makeTag(name, string=None, attrs=None):
        if attrs is not None:
            attrs = attrs.items()
        tag = bs.Tag(writer,name,attrs)
        if string is not None:
            tag.append(bs.NavigableString(string))
        return tag
    seenTags = set()
    def parseFolder(inTag,outTag):
        '''Parse the subtree rooted at inTag and update the subtree rooted at
        outTag with the extracted data.
        '''
        for subtag in inTag.findAll(['a','h3']):
            # XXX: hash(tag) is broken in BeautifulSoup, so use the ids
            if id(subtag) not in seenTags:
                seenTags.add(id(subtag))
                if subtag.name == 'a':     # extract url
                    outTag.append(makeTag('bookmark', subtag.string,
                                          attrs={'url':subtag['href']}))
                else:
                    # extract the folder's name from <h3>
                    newFolder = makeTag('folder', attrs={'name':subtag.string})
                    # and recursively its contents from the next <dl> tag
                    outTag.append(parseFolder(subtag.findNext('dl'), newFolder))
        return outTag
    writer.append(makeTag('bookmarks', attrs={'extracted-from':path}))
    # everything is contained under the first 'dl' tag
    parseFolder(bs.BeautifulSoup(open(path)).dl, writer.bookmarks)
    return writer


if __name__ == '__main__':
    import sys
    print parseBookmarks(sys.argv[1])
