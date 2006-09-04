import UserDict
from pysqlite2 import dbapi2 as sqlite

class SQLiteDict(UserDict.DictMixin):

    #_python2sql_types = {
    #    int 	       : 'integer',
    #    long 	       : 'INTEGER',
    #    float 	       : 'REAL',
    #    str            : 'TEXT',
    #    unicode 	   : 'TEXT',
    #}

    def __init__(self, keytype, valtype, path=':memory:', tablename='Dict'):
        self._keytype, self._valtype = keytype,valtype
        self._con = sqlite.connect(path, detect_types=sqlite.PARSE_DECLTYPES)
        self._cur = self._con.cursor()
        self._cur.execute('CREATE TABLE %s (key UNIQUE, value)' % tablename)
        self._insertQuery = 'REPLACE INTO %s (key, value) values (?, ?)' % tablename
        self._selectQuery = 'SELECT value FROM %s WHERE key=?' % tablename
        self._selectKeysQuery = 'SELECT key FROM %s' % tablename
        self._deleteQuery = 'DELETE FROM %s WHERE key=?' % tablename

    def keys(self):
        self._cur.execute(self._selectKeysQuery)
        return [self._keytype(t[0]) for t in self._cur.fetchall()]

    def __setitem__(self,key,val):
        adapted = []
        for obj,protocol in (key,self._keytype), (val,self._valtype):
            adapted.append(_generic_adapt(obj,protocol))
        self._cur.execute(self._insertQuery, adapted)

    def __getitem__(self,key):
        self._cur.execute(self._selectQuery, (key,))
        result = self._cur.fetchall()
        if len(result) == 1:
            return self._valtype(result[0][0])
        raise KeyError(str(key))

    def __delitem__(self,key):
        self._cur.execute(self._deleteQuery, (key,))

    def close(self):
        self._con.commit()
        self._cur.close()
        self._con.close()

    def dump(self):
        self._cur.execute('PRAGMA table_info(Dict)')
        return self._cur.fetchall()


def _generic_adapt(obj,protocol):
    try:
        adapted = protocol(obj)
        if adapted == obj:
            return adapted
    except:
        pass
    raise TypeError('%r can not be adapted to %s' %(obj,protocol))


if __name__ == '__main__':

    d = SQLiteDict(str, float) #'urls2ids',
    print d.dump()
    print d.keys()
    d["foo"] = 12
    print d.keys()
    print d["foo"]

    d["bar"] = 13.0
    print d.values()
    del d["foo"]
    print d.items()

