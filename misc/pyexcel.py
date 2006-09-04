'''
A lightweight API to access Excel data.

There are many ways to read Excel data, including ODBC. This module uses ADODB
and has the advantage of only requiring a file name and a sheet name (no setup
required).
'''

from win32com.client import Dispatch

class ExcelDocument(object):
    '''An Excel document representation.'''

    def __init__(self,filename):
        self.connection = Dispatch('ADODB.Connection')
        self.connection.Open('PROVIDER=Microsoft.Jet.OLEDB.4.0;' +
                             'DATA SOURCE=%s;' % filename +
                             'Extended Properties="Excel 8.0;HDR=1;IMEX=1"')

    def sheets(self):
        '''Return a list of the name of the sheets found in the document.'''
        result = []
        recordset = self.connection.OpenSchema(20)
        while not recordset.EOF:
            result.append(recordset.Fields[2].Value)
            recordset.MoveNext()
        recordset.Close()
        del recordset
        return result

    def sheet(self,name,encoding=None,order_by=None):
        '''Return a sheet object by name.

        Use sheets() to obtain a list of valid names.

        @param encoding: A character encoding name used to encode the unicode
            strings returned by Excel.
        '''
        return ExcelSheet(self,name,encoding,order_by)

    def __del__(self):
        self.close()

    def close(self):
        '''Close the Excel document. It is automatically called when the object
        is deleted.
        '''
        try:
            self.connection.Close()
            del self.connection
        except:
            pass


class ExcelSheet(object):
    '''An Excel sheet representation.'''

    # the size of the buffer of rows for __iter__. Use pagesize=-1 to buffer
    # the whole sheet in memory.
    _PAGESIZE = 128

    def __init__(self, document, name, encoding, order_by):
        self.document = document
        self.name = name
        self.order_by = order_by
        self._encoding = encoding

    def columns(self):
        '''Return the list of column names of this sheet.'''
        recordset = Dispatch('ADODB.Recordset')
        recordset.Open(u'SELECT * FROM [%s]' % self.name,
                       self.document.connection,0,1)
        try:
            return [self._encode(field.Name) for field in recordset.Fields]
        finally:
            recordset.Close()
            del recordset

    def __iter__(self):
        '''Return an iterator on the data contained in the sheet.

        Each row is returned as a dictionary with row headers as keys.
        '''
        recordset = Dispatch('ADODB.Recordset')
        recordset.Open(u'SELECT * FROM [%s] %s' % (
                        self.name,
                        self.order_by and 'ORDER BY %s' % self.order_by or ''),
                    self.document.connection,0,1)
        try:
            fields = [self._encode(field.Name) for field in recordset.Fields]
            ok = True
            while ok:
                rows = zip(*recordset.GetRows(self._PAGESIZE))
                if recordset.EOF:
                    # close the recordset as soon as possible
                    recordset.Close()
                    recordset = None
                    ok = False
                for row in rows:
                    yield dict(zip(fields, map(self._encode,row)))
        except:
            if recordset is not None:
                recordset.Close()
                del recordset
            raise

    def _encode(value):
        if isinstance(value,basestring):
            value = value.strip()
            if not value:
                value = None
            elif self._encoding and isinstance(value,unicode):
                value = value.encode(self._encoding)
        return value
