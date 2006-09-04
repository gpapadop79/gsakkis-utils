import inspect
from xml.dom.minidom import getDOMImplementation

__all__ = ['xmlify']


def xmlify(obj, name=None, writetype=True, writemodule=True, writeid=True):
    return _XMLPickler(obj, name, writetype, writemodule, writeid).doc


class _XMLPickler(object):

    _visited = {}

    def __init__(self, obj, name=None, writetype=True, writemodule=True,
                 writeid=True):
        self._writeid = writeid
        self._writetype = bool(writetype)
        self._writemodule = bool(writemodule)
        if name is None:
            name = 'Instance_%d' % id(obj)
        self.doc = getDOMImplementation().createDocument(None, None, None)
        self.doc.appendChild(self._addElement(obj, name))

    def _addElement(self, obj, name):
        elem = self.doc.createElement(name)
        # set the type or class of the object as an attribute
        try: cls = obj.__class__
        except AttributeError:
            cls = type(obj)
        if self._writetype:
            elem.setAttribute('type', cls.__name__)
        # set the module of the object as an attribute
        if self._writemodule:
            module = cls.__module__
            if module and module != '__builtin__':
                elem.setAttribute('module', module)
        # proceed according to the type of object
        #------- primitive types ---------------------------------------------
        if obj is None:
            return elem # empty element
        if isinstance(obj, (bool,int,float,long,complex)):
            elem.setAttribute('value', str(obj))
            return elem
        if isinstance(obj, basestring):
            elem.appendChild(self.doc.createTextNode(obj))
            return elem
        #------- compound types ----------------------------------------------
        _id = str(id(obj))
        if _id in _XMLPickler._visited:
            elem = self.doc.createElement(name)
            if self._writeid:
                elem.setAttribute('refid', _id)
            return elem
        _XMLPickler._visited[_id] = obj
        if self._writeid:
            elem.setAttribute('id', _id)
        #------- sequence types ----------------------------------------------
        if isinstance(obj, _sequenceTypes):
            for item in obj:
                elem.appendChild(self._addElement(item, 'item'))
        #------- mapping types -----------------------------------------------
        elif isinstance(obj, dict):
            for key,value in obj.iteritems():
                entry = elem.appendChild(self.doc.createElement('entry'))
                entry.appendChild(self._addElement(key, 'key'))
                entry.appendChild(self._addElement(value, 'value'))
        #------- class types -------------------------------------------------
        elif inspect.isclass(obj):
            elem.setAttribute('name', obj.__name__)
            elem.setAttribute('module', obj.__module__)
            if obj.__doc__:
                elem.setAttribute('doc', obj.__doc__)
            for attr,value in _iterDataMembers(obj):
                elem.appendChild(self._addElement(value, attr))
        #------- instance types ----------------------------------------------
        else:
            # store the initargs, if present
            if hasattr(obj, '__getinitargs__'):
                args = obj.__getinitargs__()
                elem.appendChild(self._addElement(args, '__getinitargs__'))

            if hasattr(obj, '__getstate__'):
                elem.appendChild(self._addElement(obj.__getstate__(),
                                                  '__getstate__'))
            else:
                for attr,value in _iterDataMembers(obj):
                    elem.appendChild(self._addElement(value, attr))
        return elem



def _iterDataMembers(obj):
    try: items = obj.__dict__.iteritems()
    except AttributeError:
        items = [(attr,getattr(obj,attr))
                  for attr in dir(obj) if hasattr(obj,attr)]
    for attr,value in items:
        if not (attr.startswith('__') and attr.endswith('__')):
            if not (inspect.isroutine(value) or inspect.isdatadescriptor(value)):
                yield attr,value


_sequenceTypes = [tuple,list]
# python 2.3+
try: import sets
except ImportError: pass
else: _sequenceTypes.append(sets.BaseSet)
# python 2.4+
try: _sequenceTypes.append(set)
except NameError: pass
else: _sequenceTypes.append(frozenset)
_sequenceTypes = tuple(_sequenceTypes)
