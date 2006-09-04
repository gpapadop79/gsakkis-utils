'''Yet another command line parser.'''

__author__ = "George Sakkis <gsakkis@rutgers.edu>"

import getopt, sys, os, re, cStringIO
from getopt import GetoptError
from common import uniq
import indent

class Flag(object):
    def __init__(self, switches, description=""):
        self.description = description
        if isinstance(switches, str): self.switches = [switches]
        else:                         self.switches = list(switches)

class Option(Flag):
    def __init__(self, switches, description="", argName=None, argType=str,
                 defaultVal=None, minOccurences=0, maxOccurences=1,
                 optionalArg=False):
        super(Option,self).__init__(switches,description)
        if argName==None: argName = argType.__name__
        self.argName = argName
        self.argType = argType
        self.defaultVal = defaultVal
        self.minOccurences = minOccurences
        self.maxOccurences = maxOccurences
        self.optionalArg = optionalArg

class OptionParser(object):
    '''Command line argument parser, built on top of getopt.'''

    def __init__(self,progName=os.path.basename(sys.argv[0])):
        self.__progName = progName
        self.__getOptString = ""
        self.__longOpts = []    
        self.__switches = {}
        self.__groups = []
    
    def getOptions(self): return uniq(self.__switches.values())

    def getGroups(self): return self.__groups

    def setGroup(self,description,*options): 
        self.set(options)
        self.__groups.append((description,options))
        
    def parseOptions(self,args):
        # initialization
        switchesToValues = {}
        for switch in self.__switches:
            switchesToValues[switch] = []
        # parse args with getopt
        (opts, nonopts) = getopt.gnu_getopt(args, self.__getOptString,
                                            self.__longOpts)
        opts = [(switch[switch.rfind('-',0,2)+1:], val)
                for (switch,val) in opts]
        for (switch,value) in opts:
            option = self.__switches[switch]
            if isinstance(option,Option) and option.argType != str:
                value = option.argType(value)
            for synonym in option.switches:
                switchesToValues[synonym].append(value)
        # set default values for unset switches 
        for (switch, option) in self.__switches.iteritems():
            if isinstance(option,Option) and \
                          option.defaultVal!=None and \
                          len(switchesToValues[switch]) == 0:
                default = option.argType(option.defaultVal)
                for synonym in option.switches:
                    switchesToValues[synonym].append(default)
        # check cardinality constraints
        for (switch,option) in self.__switches.iteritems():
            if isinstance(option,Option):
                min, max = option.minOccurences, option.maxOccurences
            else:
                min, max = 0, 1
            occured = len(switchesToValues[switch])
            if min <= occured <= max:
                # remove unset switches
                if occured == 0:
                    del switchesToValues[switch]
                # make scalar the values of switches that don't expect
                # multiple arguments
                elif max == 1:
                    switchesToValues[switch] = switchesToValues[switch][0]
            else:
                raise getopt.GetoptError(
                    "option '%s' is set %d times "
                    "(it should be set between %d and %d)"
                    % (_dashAdder(switch),occured,min,max), switch)
        return (switchesToValues,nonopts)

    def usage(self, title=None):
        output=cStringIO.StringIO()
        if title == None: title = "Usage: %s [options]" % self.__progName
        print >> output, title
        def printOptions(description, options):
            print >> output, "* %s" % description
            required,optional = self.__prettyPrint(*self.__splitOptions(options))
            if len(required) > 0:
                print >> output, "  Required options:"
                print >> output, os.linesep.join(required)
            if len(optional) > 0:
                if len(required) > 0:
                    print >> output, "  Other options:"
                print >> output, os.linesep.join(optional)            
        # print groupped options first
        grouppedOptions = []
        for description,options in self.__groups:
            grouppedOptions += options
            printOptions(description,options)
        # and then the ungrouped ones
        ungrouppedOptions = self.getOptions()
        for grouppedOption in grouppedOptions:
            try: ungrouppedOptions.remove(grouppedOption)
            except ValueError: pass
        if len(ungrouppedOptions) > 0:
            description = len(grouppedOptions) > 0 and "Miscellaneous" or "Options"
            printOptions(description,ungrouppedOptions)
        return output.getvalue()
    
    def set(self, *options):
        for option in options:
            if option in self.__switches.values(): 
                return
            if not isinstance(option,Option):
                def shortSwitchCode(switch): self.__getOptString += switch
                def longSwitchCode(switch): self.__longOpts.append(switch)
            elif not option.optionalArg:
                def shortSwitchCode(switch): self.__getOptString += switch + ':'
                def longSwitchCode(switch): self.__longOpts.append(switch + '=')
            else:
                def shortSwitchCode(switch): 
                    self.__getOptString += switch + '::'
                    raise NotImplementedError("Optional arguments not implemented yet")
                def longSwitchCode(switch):
                    raise NotImplementedError('Optional arguments not implemented yet')
            for switch in option.switches:
                if switch in self.__switches:
                    raise getopt.GetoptError("switch '%s' is already defined"
                                             % _dashAdder(switch), switch)
                if len(switch) == 1:  shortSwitchCode(switch)
                else:                 longSwitchCode(switch)
                self.__switches[switch] = option

    def __prettyPrint(self,required,optional):
        rows = []
        for optionKind in (required,optional):
            # column[0]: the option's switch(es); column[1]: the option's description
            columns = [[],[]] 
            for option in optionKind:
                buffers = [', '.join(map(_dashAdder,option.switches)),
                           option.description]
                if isinstance(option,Option):
                    if len(option.switches) > 1:
                        buffers[0] = '(%s)' % buffers[0]
                    arg = '<%s>' % option.argName
                    if option.optionalArg:
                        arg = '[%s]' % arg
                    buffers[0] = '%s %s' % (buffers[0],arg)
                    if option.defaultVal != None:
                        buffers[1] = '%s [default=%s]' % (buffers[1],
                                                          option.defaultVal)
                for i in xrange(0,len(columns)):
                    columns[i].append(buffers[i])
            # create rows from columns and sort them
            # ignore leading non-alphabetic characters for sorting
            m = re.compile(r'^\W*')    
            tmprows = [[(m.sub('',s).lower(),s) for s in row]
                       for row in zip(*columns)]
            tmprows.sort()
            rows += [ [t[1] for t in row] for row in tmprows]
        optionRows = indent.indent(rows, delim='   ',
                                   justify="left", prefix=4*' ').splitlines()
        return splitByLengths(optionRows, [len(required),len(optional)])

    def __splitOptions(self,options):
        # tell apart required and optional switches
        required = []; optional = []
        for option in options:
            if isinstance(option,Option) and option.minOccurences > 0:
                required.append(option)
            else:
                optional.append(option)
        return (uniq(required), uniq(optional))


def _dashAdder(switch):
    return len(switch) == 1 and '-' + switch or '--' + switch


def splitByLengths(iterable, lengths):
    '''Forms subsequences whose lengths are determined by the second
       argument by drawing elements from the iterable, so that their
       concatenation would give the original sequence if the sum of the lengths
       given is greater or equal to the iterable's length. 
       If the sum of lengths is greater, elements of the iterable are added to
       the subsequences until they are exhausted. For example: 
           splitByLengths(('a','b','c','d','e'),
                          (2,1,0,3)) == [('a','b'),('c',),(),('d','e')]
       The last subsequence has length 2 instead of 3.
       If the sum of lengths N is smaller, the first N elements of the
       iterable are added to the subsequences. For example
       splitByLengths(('a','b','c','d','e'), (2,1)) == [('a','b'),('c',)]
       - iterable: An iterable
       - lengths: An iterable over non-negative integers.'''
    iterator = iter(iterable)
    def makeSequence(length):
        if length < 0: raise ValueError, "negative length %d given" % length
        subsequence = []
        for i in xrange(length):
            try: subsequence.append(iterator.next())
            except StopIteration: break
        return subsequence
    return map(makeSequence,lengths)

#test_splitByLengths():
#    import operator,random
#    seq = [chr(ord('a') + i) for i in xrange(26)]
#    for i in xrange(10000):
#        lengthsList = []
#        summed = random.randrange(len(seq)//2, 3*len(seq)//2)
#        ##print "Sum: %d  ==> " %summed,
#        while summed>0:
#            lengthsList.append(random.randrange(summed+1))
#            summed -= lengthsList[-1]
#        random.shuffle(lengthsList)
#        ##print lengthsList
#        assert reduce(operator.add, splitByLengths(seq, lengthsList)) == seq[:sum(lengthsList)]

####################### main - demonstrate OptionParser ######################

if __name__ == '__main__':
    def configureParser(parser):
        # simple flag option
        parser.set(Flag("v", "Verbose mode"))
        
        # flag option with synonym
        parser.set(Flag(("h","help"), "Display help and exit"))
        
        # optional switched with required argument and integer type
        # (without default value)
        omax = Option(("M","max"),
                      "Maximum number of transactions per second",
                      argType=int)
        omin = Option(("m","min"),
                      "Minimum number of transactions per second",
                      argType=int)
        
        # group the last two options together
        parser.setGroup("Transactions",omax,omin)
        # optional switch with required argument and default value
        parser.set(Option(("o","output"), "Output directory",
                          defaultVal="/usr/tmp/"))
        # required option
        parser.set(Option(["site","url"], "A starting URL", "url",
                          minOccurences=1, maxOccurences=sys.maxint))
        ## optional switch with optional argument
        ##parser.set(Option("log", "Logfile - no argument for logging to "
        ##                  "standard error", "file", optionalArg=True))
        return parser

    p = OptionParser()
    configureParser(p)
    print p.usage()        
    if len(sys.argv) == 1:
        sys.argv[1:] = ("-vh --site www.amazon.com something "
                        "--url=http://192.168.170.27 -M100").split()
    print "Command line:", ' '.join(sys.argv)
    (opts,nonopts) = p.parseOptions(sys.argv[1:])
    ##print opts
    
    # check if a specific flag has been set
    print "Arguments:",sys.argv[1:]
    print "Verbose mode:", "v" in opts

    # get the value of a specific Option - returns null if the option is not
    # included in args and if no default value has been set for the option
    if "maximum" in opts: print "Maximum-1 is ", opts["max"]-1

    # for an option with a required argument and a default value, 
    # the latter is returned if the option is not included in args
    print "Output directory:", opts["output"]
    
    # all synonyms of an option refer to the same value
    print "Url:", opts["url"]
    print "Site:", opts["site"]

    # get the non-option arguments
    print "Non options:", nonopts

    #import inspect
    #(formals,_,_,locals) = inspect.getargvalues(inspect.currentframe())
    #otherArgs = {}
    #for formal in formals: otherArgs[formal] = locals[formal]
    #for x in "self","switches","description": del otherArgs[x]

