'''An unmodifiable hashable dict.'''

__author__ = 'George Sakkis <gsakkis@rutgers.edu>'
__all__ = ['frozendict', 'Empty']

import sys

# in python 2.2+, dict can be subclassed; otherwise use UserDict
if sys.version_info[:2] < (2,2):
    from UserDict import UserDict as _base
else:
    _base = dict



class frozendict(_base):
    '''An unmodifiable (and thus hashable) dict.'''

    def __init__(self, keyvalues=(), **other):
        _base.__init__(self)
        try: keyvalues = keyvalues.items()
        except AttributeError: pass
        for k,v in keyvalues:
            _base.__setitem__(self,k,v)
        _base.update(self,other)
        self._hash = hash(tuple(self.items()))

    def __hash__(self): return self._hash
    def __setitem__(self,key,value): self._raise()
    def __delitem__(self,key): self._raise()
    def clear(self): self._raise()
    def setdefault(self,k,default=None): self._raise()
    def popitem(self): self._raise()
    def update(self,other): self._raise()
    def _raise(self): raise TypeError('frozendicts are immutable')

Empty = frozendict()
