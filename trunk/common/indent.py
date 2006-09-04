'''
A function to pretty print tables in plain text mode and helper text line
wrappers.
'''

import os
import re
import math
import cStringIO

__author__ = "George Sakkis <gsakkis@rutgers.edu>"
__all__ = ["indent", "wrap_onspace", "wrap_onspace_strict", "wrap_always"]

##############################################################################

def indent(rows, hasHeader=False, headerChar='-', delim=' | ', justify='left',
           separateRows=False, prefix='', postfix='', wrapfunc=lambda x:x):
    '''Indents a table in equally lengthed columns.

    Demo:
        >>> from indent import indent, _demo_table
        >>> table = _demo_table(getLabels=True)
        >>> for row in table:
        ...     print row
        ('First Name', 'Last Name', 'Age', 'Position')
        ['John', 'Smith', '24', 'Software Engineer']
        ['Mary', 'Brohowski', '23', 'Sales Manager']
        ['Aristidis', 'Papageorgopoulos', '28', 'Senior Reseacher']

        >>> print indent(table)
        First Name | Last Name        | Age | Position
        John       | Smith            | 24  | Software Engineer
        Mary       | Brohowski        | 23  | Sales Manager
        Aristidis  | Papageorgopoulos | 28  | Senior Reseacher

        >>> print indent(table,
        ...              hasHeader  = True,
        ...              justify    = 'center',
        ...              prefix     = '>  ',
        ...              postfix    = '  <',
        ...              delim      = '  #  ',
        ...              headerChar = '~')
        >  First Name  #     Last Name      #  Age  #       Position      <
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        >     John     #       Smith        #   24  #  Software Engineer  <
        >     Mary     #     Brohowski      #   23  #    Sales Manager    <
        >  Aristidis   #  Papageorgopoulos  #   28  #   Senior Reseacher  <

        >>> print indent(table,
        ...              hasHeader = True,
        ...              wrapfunc  = lambda x: wrap_onspace(x,10))
        First Name | Last Name        | Age | Position
        -----------------------------------------------
        John       | Smith            | 24  | Software
                   |                  |     | Engineer
        Mary       | Brohowski        | 23  | Sales
                   |                  |     | Manager
        Aristidis  | Papageorgopoulos | 28  | Senior
                   |                  |     | Reseacher

    @param rows: A sequence of sequences of items, one sequence per row of
        the table.
    @param hasHeader: True if the first row consists of the columns' names.
    @param headerChar: Character to be used for the row separator line
        (if hasHeader==True or separateRows==True).
    @param delim: The column delimiter.
    @param justify: Determines how are data justified in their column.
        Valid values are 'left','right' and 'center'.
    @param separateRows: True if rows are to be separated by a line
        of 'headerChar's.
    @param prefix: A string prepended to each printed line.
    @param postfix: A string appended to each printed line.
    @param wrapfunc: A function f(text) for wrapping each element of the table.
        By default, no wrapping is performed.
    '''
    # closure for breaking logical rows to physical, using wrapfunc
    def rowWrapper(row):
        wrappedRows = map(None,
                          *[wrapfunc(str(item)).split(os.linesep)
                            for item in row])
        # replace None with empty strings
        newRows = []
        for row in wrappedRows:
            # row may be a tuple of items of a string
            if isinstance(row,tuple):
                  newRows.append([item or '' for item in row])
            else: newRows.append((row,))
        return newRows
    # break each logical row into one or more physical ones
    logicalRows = [rowWrapper(row) for row in rows]
    #print "logicalRows: ",logicalRows
    # columns of physical rows
    columns = zip(*sum(logicalRows,[]))
    # get the maximum of each column by the string length of its items
    maxWidths = [max([len(str(item)) for item in column])
                 for column in columns]
    delim = delim.expandtabs()
    rowSeparator = headerChar * \
                   (sum(maxWidths) + len(delim)*(len(maxWidths)-1) +
                    len(prefix) + len(postfix))
    # select the appropriate justify method
    justify = {'left':str.ljust, 'right':str.rjust,
               'center':str.center }[justify.lower()]
    output=cStringIO.StringIO()
    if separateRows: print >> output, rowSeparator
    for physicalRows in logicalRows:
        for row in physicalRows:
            print >> output, prefix \
                + delim.join([justify(str(item),width)
                              for (item,width) in zip(row,maxWidths)]) \
                + postfix
        if separateRows or hasHeader:
            print >> output, rowSeparator; hasHeader=False
    return output.getvalue().rstrip(os.linesep)

# written by Mike Brown
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/148061
def wrap_onspace(text, width):
    '''
    A word-wrap function that preserves existing line breaks
    and most spaces in the text. Expects that existing line
    breaks are posix newlines.

    @param text: The string to be wrapped.
    @param width: The maximum length of each wrapped line.
    '''
    return reduce(lambda line, word, width=width: '%s%s%s' %
                  (line,
                   ' \n'[(len(line[line.rfind('\n')+1:])
                         + len(word.split('\n',1)[0]
                              ) >= width)],
                   word),
                  text.split(' ')
                 )

def wrap_onspace_strict(text, width):
    '''Similar to L{wrap_onspace}, but enforces the width constraint.

    Words longer than width are split.

    @param text: The string to be wrapped.
    @param width: The maximum length of each wrapped line.
    '''
    wordRegex = re.compile(r'\S{'+str(width)+r',}')
    return wrap_onspace(wordRegex.sub(lambda m: wrap_always(m.group(),width),
                                      text),width)

def wrap_always(text, width):
    '''A simple word-wrap function that wraps text on exactly width characters.

    It doesn't split the text in words.

    @param text: The string to be wrapped.
    @param width: The maximum length of each wrapped line.
    '''
    return os.linesep.join([text[width*i:width*(i+1)]
                            for i in xrange(int(math.ceil(
                                len(text)/float(width))))])


def _demo_table(getLabels=False):
    labels = ('First Name', 'Last Name', 'Age', 'Position')
    data = \
    '''John,Smith,24,Software Engineer
       Mary,Brohowski,23,Sales Manager
       Aristidis,Papageorgopoulos,28,Senior Reseacher'''
    table = [row.strip().split(',')  for row in data.splitlines()]
    if getLabels: table.insert(0,labels)
    return table

if __name__ == '__main__':
    import doctest; doctest.testmod()
