from __future__ import division, generators
from cStringIO import StringIO

from common import sorted,sum

__author__ = 'George Sakkis <gsakkisATrutgersDOTedu>'
__all__ = ['Problem', 'Page', 'Picture']

AR_LIMIT = 0.02


#====== Rectangle ============================================================

class Rectangle(object):
    def __init__(self, width, height):
        self._w = width
        self._h = height
        self._minX = self._minY = None

    #----- properties --------------------------------------------------------

    width = property(lambda self: self._w)
    height = property(lambda self: self._h)

    minX = property(lambda self: self._minX)
    maxX = property(lambda self: self._minX + self._w)
    minY = property(lambda self: self._minY)
    maxY = property(lambda self: self._minY + self._h)

    area = property(lambda self: self._w * self._h)
    aspectRatio = property(lambda self: self._w > self._h
                                        and self._w / self._h
                                        or  self._h /self._w)

    #----- accessors ---------------------------------------------------------

    def contains(self, other):
        return (self.minX <= other.minX and self.maxX >= other.maxX and
                self.minY <= other.minY and self.maxY >= other.maxY)

    def overlaps(self, other):
        return (self.minX < other.maxX and self.maxX > other.minX and
                self.minY < other.maxY and self.maxY > other.minY)

    #----- mutators ----------------------------------------------------------

    def place(self, minX, minY):
        self._minX = minX; self._minY = minY

    def rotate(self):
        self._w, self._h = self._h, self._w

    def resizeToWidth(self, width):
        self._h = int(self._h * width / self._w)
        self._w = width

    def resizeToHeight(self, height):
        self._w = int(self._w * height / self._h)
        self._h = height

    def stretch(self, width=None, height=None):
        if width is not None: self._w = width
        if height is not None: self._h = height

    #def _containsPoint(self, x, y):
    #    return (self._minX <= x <= self._minX + self._w and
    #            self._minY <= y <= self._minY + self._h)


#====== Picture ==============================================================

class Picture(Rectangle):

    def __init__(self, label, width, height):
        Rectangle.__init__(self,width,height)
        self.label = label
        ar = self.aspectRatio
        self.minAspectRatio = ar - AR_LIMIT
        self.maxAspectRatio = ar + AR_LIMIT

    #def __hash__(self): return hash(self.label)
    #def __eq__(self, other): return self.label == other.label
    #def __ne__(self, other): return self.label != other.label

    #label = property(lambda self: self._label)


#====== Page =================================================================

class Page(Rectangle):

    def __init__(self, width, height):
        Rectangle.__init__(self,width,height)
        self._minArea = int(width * height * 0.01)
        self._pictures = {}

    #----- Operators ---------------------------------------------------------

    def placePicture(self, picture, minX, minY):
        self._pictures[picture.label] = picture
        picture.place(minX,minY)
        assert self._layoutCheck(picture)

    def rotatePicture(self, picture, times=1):
        picture.rotate(times)
        assert self._layoutCheck(picture)

    def resizeToWidthPicture(self, picture, width):
        picture.resizeToWidth(width)
        assert self._fullCheck(picture)

    def resizeToHeightPicture(self, picture, height):
        picture.resizeToHeight(height)
        assert self._fullCheck(picture)

    def stretchPicture(self, picture, width=None, height=None):
        picture.stretch(width,height)
        assert self._fullCheck(picture)

    #----- Constraints -------------------------------------------------------

    def _layoutCheck(self, picture):
        if not self.contains(picture):
            return False
        for otherPicture in self._pictures.itervalues():
            if otherPicture is not picture:
                if picture.overlaps(otherPicture):
                    return False
        return True

    def _fullCheck(self, picture):
        # check the layout, size and ratio constraints
        ar = picture.aspectRatio
        return (picture.minAspectRatio <= ar <= picture.maxAspectRatio
                and picture.area >= self._minArea
                and self._layoutCheck(picture))

    def __str__(self):
        output = StringIO()
        attrs = 'label width height minX minY'.split()
        for label,pic in sorted(self._pictures.iteritems()):
            print >> output, ' '.join([str(getattr(pic,attr))
                                       for attr in attrs])
        return output.getvalue().strip()


#====== Problem ==============================================================

class Problem(object):

    def __init__(self, filename):
        infile = open(filename)
        self._page = Page(*map(int, infile.readline().split()[1:]))
        self._picturesDict = {}
        for line in infile.readlines():
            label,width,height = line.split()
            self._picturesDict[label] = Picture(label, int(width), int(height))
        self._page._pictures.update(self._picturesDict)

    page = property(lambda self: self._page)
    pictures = property(lambda self: self._picturesDict.values())

    def objectiveFunction(self):
        return page.area - sum([picture.area for picture in self.pictures])

##====== Problem ==============================================================
#
#def sum(
#
#def sorted(seq, key=None):
#    if key is not None:
#        seq = [(key(x),x) for x in seq]
#        seq.sort()
#        return [x for k,x in seq]
#    else:
#        seq = list(seq)
#        seq.sort()
#        return seq
