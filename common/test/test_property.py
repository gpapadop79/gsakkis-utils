from math import radians, degrees, pi
from common import Property


class Angle(object):
    def __init__(self,rad):
        self._rad = rad

    @Property
    def rad():
        '''The angle in radians'''
        def fget(self):
            return self._rad
        def fset(self,angle):
            if isinstance(angle,Angle): angle = angle.rad
            self._rad = float(angle)

    @Property
    def deg():
        '''The angle in degrees'''
        def fget(self):
            return degrees(self._rad)
        def fset(self,angle):
            if isinstance(angle,Angle): angle = angle.deg
            self._rad = radians(angle)


def testProperty():
    a = Angle(pi/3)
    assert a.rad == pi/3 and almostEquals(a.deg, 60)
    a.rad = pi/4
    assert a.rad == pi/4 and almostEquals(a.deg, 45)
    a.deg = 30
    assert a.rad == pi/6 and almostEquals(a.deg, 30)
    assert Angle.rad.__doc__ == '''The angle in radians'''
    assert Angle.deg.__doc__ == '''The angle in degrees'''


def almostEquals(x,y):
    return abs(x-y) < 1e-9
