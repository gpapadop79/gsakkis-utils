# todo:
# ? distinguish chatters (map nick -> person)

import sys, os, re, shutil
from warnings import warn


#======= MircLog ==============================================================

class MircLog(file):

    def __init__(self, *args, **kwds):
        file.__init__(self,*args,**kwds)
        self.sessions = []
        matchLine = MultiMatcher(r'^<(.+?)>(.*)',
                                 r'\*\s*(\S+)(.*)').match
        matchSession = re.compile(r'^Session (\w+):(.*)').match
        numLines = 0
        for num,line in enumerate(self):
            line = line.strip()
            if not line: continue
            if self.sessions:
                session = self.sessions[-1]
            else:
                session = MircLog.Session(None)
            try:
                nick, message = matchLine(line).groups()
                session.add(num,nick,message)
            except AttributeError:
                try: field,value = matchSession(line).groups()
                except AttributeError: continue
                if field == 'Start':
                    self.sessions.append(MircLog.Session(value))
                elif field == 'Ident':
                    session.setIdent(value)
                elif field == 'Close':
                    session.end = value
                elif field == 'Time': # ignore
                    pass
                else:
                    warn('Unrecognized field: %s' % field)
        self.numlines = num

    def nicks(self):
        return sum([session.nicks() for session in self.sessions], [])

    #def myNicks(self):
    #    return sum([session.myNicks() for session in self.sessions], [])
    #
    #def herNicks(self):
    #    return sum([session.herNicks() for session in self.sessions], [])

    #======= MircLog.Session ==================================================

    class Session(object):
        def __init__(self, start, end=None):
            self.start = start
            self.end = end
            self._logDict = {}

        def __getitem__(self,nick):
            return self._logDict[nick]

        def nicks(self):
            return self._logDict.keys()

        #def myNicks(self):
        #    nicks = self.nicks()
        #    nicks.remove(self.ident)
        #    return nicks
        #
        #def herNicks(self):
        #    return [self.ident]

        def add(self,num,nick,message):
            entry = num,message
            try: self._logDict[nick].append(entry)
            except KeyError: self._logDict[nick] = [entry]

        def setIdent(self,ident):
            self.ident = ident


#======= MultiMatcher =========================================================

class MultiMatcher(object):

    def __init__(self, *regexes):
        self._regexes = map(re.compile, regexes)

    def match(self, text):
        return self._cascade(text, re.match)

    def search(self, text):
        return self._cascade(text, re.search)

    def _cascade(self, text, regexMethod):
        for regex in self._regexes:
            m = regexMethod(regex,text)
            if m is not None:
                return m
        return None


#======= processDir ===========================================================

def processDir(dir, filters, actions, openFile = open):
    backup = os.path.join(os.path.pardir, ".backup")
    if not os.path.exists(backup):
        os.mkdir(backup)
    for num,filename in enumerate(os.listdir(dir)):
        filename = os.path.join(dir,filename)
        if not os.path.isfile(filename):
            continue
        f = openFile(filename)
        for filter in filters:
            if not filter(f): break
        else:
            for action in actions:
                try: action(f)
                except Exception, e: warn(e)


#======= MircLog filters ======================================================

_getMax = max
_getMin = min

def lineNumFilterFactory(min=0, max=sys.maxint):
    return lambda mircLog: min <= mircLog.numlines <= max

def sentenceNumFilterFactory(min=0, max=sys.maxint):
    def filter(mircLog):
        minSentences = []
        for session in mircLog.sessions:
            nicks = session.nicks()
            if nicks:
                minSentences.append(_getMin([len(session[nick])
                                             for nick in nicks]))
        if minSentences:
            return min <= _getMax(minSentences) <= max
        else: return False
    return filter

def changedNickFilter(mircLog):
    for session in mircLog.sessions:
        nicks = session.nicks()
        if len(nicks) > 2:
            print mircLog.name, [(nick,len(session[nick])) for nick in nicks]
            return True

def onlyOneTalkingFilter(mircLog):
    return len(mircLog.nicks()) < 2


#======= MircLog actions ======================================================

def printAction(mircLog):
    print os.path.abspath(mircLog.name), mircLog.numlines

def moveActionFactory(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)
    return lambda mircLog: shutil.move(mircLog.name, dir)


#======= main =================================================================

if __name__ == '__main__':
    for dir in (sys.argv[1:] or ['.']):
        processDir(dir,
                   filters=[sentenceNumFilterFactory(max=4)],
                   #actions=[printAction],
                   actions=[changedNickFilter],
                   #actions=[moveActionFactory(os.path.join(dir,"trash2"))],
                   openFile=MircLog)
