#!/usr/bin/env python

'''A tool to generate XML DTDs.

DTDGenerator is a program that takes an XML document as input and produces a
Document Type Definition (DTD) as output.

The aim of the program is to give a quick start in writing a DTD. The DTD is
one of the many possible DTDs to which the input document conforms. Typically,
you will want to examine the DTD and edit it to describe your intended
documents more precisely.

This is a python implementation of the homonymous tool by Michael H. Kay,
available from U{http://saxon.sourceforge.net/dtdgen.html}.
'''

#TODO: refactoring, documentation

import sys, os
from cStringIO import StringIO
from collections import deque
from cElementTree import iterparse
from elementtree.SimpleXMLWriter import escape_attrib
from xml.parsers.xmlproc.xmlutils import matches, reg_name, reg_nmtoken

__author__ = 'George Sakkis <gsakkis@rutgers.edu>'

#===== Configuration constants ===============================================

# minimum number of appearances of an attribute to be candidate for an
# enumeration type
MIN_ENUMERATION_INSTANCES = 10

# maximum number of distinct attribute values for the attribute to be
# candidate for an enumeration type
MAX_ENUMERATION_VALUES = 20

# an attribute will be regarded as an enumeration only if the number of
# instances divided by the number of distinct values is >= this constant
MIN_ENUMERATION_RATIO = 3.0

# minimum number of attributes that must appear, with the same value each
# time, for the value to be regarded as FIXED
MIN_FIXED = 5

# minumum number of attribute values that must appear for the attribute
# to be regarded as an ID value
MIN_ID_VALUES = 10

# maximum number of attribute values to be saved while checking for uniqueness
MAX_ID_VALUES = 100000


#===== InferredDTD ===========================================================

class InferredDTD(object):

    def __init__(self, source):
        self.elements = []
        # map element names to ElementTypes
        elemDict = {}
        # elements currently open
        elemStack = []
        # map (father-name, child-name) to _childInfo
        childInfoDict = {}
        namespaces = deque([('xml','http://www.w3.org/XML/1998/namespace')])
        pendingNamespaces = []
        for event,elem in iterparse(source, events=('start', 'end',
                                                    'start-ns', 'end-ns')):
            if event == 'start-ns':
                namespaces.appendleft(elem)
                pendingNamespaces.append(elem)

            elif event == 'end-ns':
                namespaces.popleft()

            elif event == 'start':
                # add the namespace declarations as attributes
                for prefix,url in pendingNamespaces:
                    attr = prefix and 'xmlns:%s' % prefix or 'xmlns'
                    elem.attrib[attr] = escape_attrib(url)
                del pendingNamespaces[:]
                # convert name from clark format to prefix:local
                name = _clark_to_orig(elem.tag,namespaces)
                elemType = elemDict.get(name)
                if elemType is None:
                    elemType = ElementType(name)
                    elemDict[name] = elemType
                    self.elements.append(elemType)
                elemType._occurrences += 1
                # update atttibute declarations
                for attr,value in elem.items():
                    # convert attribute names from clark format to prefix:local
                    elemType.updateAttribute(_clark_to_orig(attr,namespaces),value)
                # keep track of the nesting and sequence of child elements
                if elemStack:
                    parentEntry = elemStack[-1]
                    # for sequencing, we're interested in consecutive groups
                    # of the same child element type
                    isFirstInGroup = parentEntry.latestChild != name
                    if isFirstInGroup:
                        parentEntry.latestChild = name
                        parentEntry.sequenceNumber += 1
                    # check if we've seen this child of this parent before
                    parent = parentEntry.elemType
                    childInfo = childInfoDict.get((parent.name,name))
                    if childInfo is None:
                        # this is the first time we've seen this child
                        # belonging to this parent. if the child is not on
                        # the first instance of the parent, then we allow it
                        # as an optional element
                        childInfo = _ChildInfo(name, parent._occurrences>1)
                        childInfoDict[parent.name,name] = childInfo
                        parent._children.append(childInfo)
                    elif (
                        # we've seen this child before: check if it makes
                        # parent non-consecutive
                        parent._occurrences == 1 and isFirstInGroup
                        # check whether the position of this group of children in
                        # this parent element is the same as its position in
                        # previous instances of the parent.
                        or len(parent._children) <= parentEntry.sequenceNumber
                        or parent._children[parentEntry.sequenceNumber].name != name):
                            parent._sequenced = False
                    # if there's more than one child element, mark it as repeatable
                    if not isFirstInGroup:
                        childInfo.repeatable = True
                #fi elemStack
                elemStack.append(_StackEntry(elemType))

            elif event == 'end':
                entry = elemStack.pop()
                elemType = entry.elemType
                for txt in elem.text, elem.tail:
                    if txt is not None and not txt.isspace():
                        elemType._hasCharacterContent = True
                        break
                # check that all expected children are accounted for.
                # If the number of child element groups in this parent element
                # is less than the number in previous elements, then the
                # absent children are marked as optional
                if elemType._sequenced:
                    for c in elemType._children[entry.sequenceNumber+1:]:
                        c.optional = True
                elem.clear()

    def __str__(self):
        return os.linesep.join(map(str, self.elements))


#===== ElementType ===========================================================

class ElementType(object):
    '''A data structure to keep information about element types.'''

    def __init__(self, name):
        self.name = name
        self._hasCharacterContent = False
        self._attrTypes = {}
        self._occurrences = 0
        self._sequenced = True
        self._children = []

    def attributes(self):
        return self._attrTypes.values()

    def attribute(self,name):
        return self._attrTypes[name]

    def updateAttribute(self, name, value):
        attr = self._attrTypes.get(name)
        if attr is None:
           attr = self._attrTypes.setdefault(name, AttributeType(name,self))
        attr.update(value)

    def __str__(self):
        out = StringIO()
        childKeys = [x.name for x in self._children]
        if not childKeys:
            # EMPTY or PCDATA
            print >> out, '<!ELEMENT %s %s>' % (self.name,
                                                self._hasCharacterContent and
                                                '(#PCDATA)' or 'EMPTY')
        elif self._hasCharacterContent:
            # MIXED content
            print >> out, '<!ELEMENT %s (#PCDATA | %s)*>' % (self.name,
                                                        ' | '.join(childKeys))
        else:
            # only subelements
            if self._sequenced:
                # all elements of this type have the same child elements
                # in the same sequence, retained in the _children vector
                strings = []
                for ch in self._children:
                    if not ch.optional:
                        if not ch.repeatable: modifier = ''
                        else:                 modifier = '+'
                    elif ch.repeatable:       modifier = '*'
                    else:                     modifier = '?'
                    strings.append('%s%s' % (ch.name, modifier))
                print >> out, '<!ELEMENT %s (%s)>' % (self.name,
                                                      ', '.join(strings))
            else:
                # the children don't always appear in the same sequence
                # so allow them to be in any order
                print >> out, '<!ELEMENT %s (%s)*>' % (self.name,
                                                       ' | '.join(childKeys))
        # print attribute declarations
        for attrType in self._attrTypes.itervalues():
            print >> out, attrType
        return out.getvalue()


#===== AttributeType =========================================================

class AttributeType(object):
    '''A data structure to keep information about attribute types.'''

    def __init__(self, name, elemType):
        self.name = name
        self.elemType = elemType
        self.values = set()
        self.unique = True
        self.allNames = True
        self.allNMTOKENs = True
        self._occurrences = 0

    def update(self, value):
        if value not in self.values:
            # We haven't seen this attribute value before
            self.values.add(value)
            # Check if attribute value is a valid name
            if self.allNames and not matches(reg_name,value):
                self.allNames = False
            # Check if attribute value is a valid NMTOKEN
            if self.allNMTOKENs and not matches(reg_nmtoken,value):
                self.allNMTOKENs = False
            # save the new value only when it's needed: if we're
            # looking for ID values or enumerated values
            if ((self.unique and self.allNames and
                 self._occurrences <= MAX_ID_VALUES)
                or len(self.values) <= MAX_ENUMERATION_VALUES):
                    self.values.add(value)
        else: # We've seen this attribute value before
            self.unique = False
        self._occurrences +=1

    def __str__(self):
        strings = [self.elemType.name,self.name]
        tokentype = self.allNMTOKENs and 'NMTOKEN' or 'CDATA'
        # if there is only one attribute value, and at least MIN_FIXED
        # occurrences of it, treat it as FIXED
        numVals = len(self.values)
        if numVals==1 and self._occurrences >= MIN_FIXED:
            singleton = iter(self.values).next()
            fixedVal = escape_attrib(singleton)
            for s in tokentype, '#FIXED', '"%s"' % fixedVal:
                strings.append(s)
        else:
            # check if it is id
            # TODO: this may give the wrong answer, we should check
            # whether the value sets of two candidate-ID attributes
            # overlap, in which case they can't both be IDs !!)
            if (self.unique
                and self.allNames # ID values must be Names
                and self._occurrences >= MIN_ID_VALUES):
                    strings.append('ID')
            # check if is it is enumeration
            elif (self.allNMTOKENs # Enumeration values must be NMTOKENs
                  and self._occurrences >= MIN_ENUMERATION_INSTANCES
                  and numVals <= self._occurrences/MIN_ENUMERATION_RATIO
                  and numVals <= MAX_ENUMERATION_VALUES):
                    strings.append('(%s)' % ' | '.join(self.values))
            else:
                strings.append(tokentype)
            # If the attribute is present on every instance of the
            # element, treat it as required
            strings.append(self._occurrences == self.elemType._occurrences
                           and '#REQUIRED' or '#IMPLIED')
        return '<!ATTLIST %s>' % ' '.join(strings)


#===== 'private' helpers =====================================================

class _ChildInfo(object):
    def __init__(self, name, optional=False, repeatable=False):
        self.__dict__.update(locals())
        delattr(self,'self')


class _StackEntry(object):
    def __init__(self, elemType, sequenceNumber=-1, latestChild=None):
        self.__dict__.update(locals())
        delattr(self,'self')


def _clark_to_orig(name, namespaces):
    if name[0] != '{':
        return name # local name
    ns, local = name[1:].split('}')
    for prefix, url in namespaces:
        if ns == url:
            return prefix and '%s:%s' % (prefix, local) or local
    raise LookupError('cannot find prefix of %r' % ns)


#=============================================================================

if __name__ == '__main__':
    print InferredDTD(sys.argv[1])
