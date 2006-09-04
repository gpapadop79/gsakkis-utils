from datetime import date
from xmlify import xmlify

class Classic:
    cvar = None
    def __init__(self, v): self._cvar = v
    def cmeth(self): pass

class NewClass(Classic,object):
    nvar = None
    def __init__(self, v): self._nvar = v
    def nmeth(self): pass
    nprop = property(lambda self: 1)

class WithInitArgs(object):
    def __getinitargs__(self): return (-1,False)

class WithGetState(object):
    def __getstate__(self): return [None,13,'goal']

class WithSlots(object):
    __slots__ = 'x','y','z'
    def __init__(self,x,y): self.x,self.y = x,y


def test():
    obj = [
        ('n'  , None),
        ('b'  , False),
        ('i'  , -3545),
        ('l'  , 485798475832348323),
        ('f'  , 0.9384e-12),
        ('c'  , 12-3j),
        ('s'  , '"Hello" <world> !'),
        ('u'  , u'\N{Copyright Sign}&'),
        ('d'  , date(2003,12,21)),
        ('DT' , date),
        ('L'  , [1,'2']),
        ('T'  , (None,3,True)),
        ('S'  , set([0,'0'])),
        ('D'  , {'x':[1], (2,True):4.7}),
        ('C'  , Classic),
        ('N'  , NewClass),
        ('CI' , Classic('hey')),
        ('NI' , NewClass('yo')),
        ('IN' , WithInitArgs()),
        ('GS' , WithGetState()),
        ('SL' , WithSlots(3.14, False)),
    ]
    get = dict(obj).__getitem__
    obj.append(('RF' , (get('L'),
                        {get('T') : (get('S'), get('u'))},
                        [get('CI'), get('D'), get('d')]
                        )))
    return obj


if __name__ == '__main__':
    from xml.dom.ext import PrettyPrint
    PrettyPrint(xmlify(test()))



#import gnosis.xml.pickle
#print gnosis.xml.pickle.XML_Pickler().dumps(Foo())
