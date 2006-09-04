# todo: refactor (design pattern)

import sys, os
import re
import optparse
from string import Template

from common.misc import beautifyOptionHelp


def main():
    option = optparse.make_option
    parser = optparse.OptionParser(
        usage = 'usage: %prog [options] classname(s)',
        option_list= [
            option('--sourcesuffix', **beautifyOptionHelp(
                   help='Source file suffix',
                   default='cpp')),

            option('--headersuffix', **beautifyOptionHelp(
                   help='Header file suffix',
                   default='hpp')),

            #option('-i', '--indentspaces',
            #       help='Number of spaces per indentation block',
            #       type='int',
            #       default=4),

            #option('-n', '--noncopyable',
            #       help='Non copyable class',
            #       action='store_true'),

            #option('-p', '--pimpl',
            #       help='Use Private Implementation (Pimpl) idiom',
            #       action='store_true'),
            #
            #option('-b', '--boost',
            #       help='Use boost libraries',
            #       action='store_true'),
            ])
    options,classes = parser.parse_args()
    for clsname in classes:
        makeTemplateFiles(clsname, **options.__dict__)



def makeTemplateFiles(clsname, **kwds):
    template = CppClassTemplate() # kwds['boost'])
    template.writeFiles(clsname, kwds['headersuffix'], kwds['sourcesuffix'])


class CppClassTemplate(object):

    def __init__(self): #, boost=False, noncopyable=False, pimpl=False
        self._headerTemplate = Template(shiftText('''
            #include <boost/utility.hpp>
            #include <boost/scoped_ptr.hpp>

            class $Class : private boost::noncopyable {
                public:
                    $Class();
                    virtual ~$Class();

                private:
                    $Class(const $Class&);
                    $Class& operator=(const $Class&);

                    // PIMPL idiom
                    class _Implementation;
                    boost::scoped_ptr<_Implementation> _impl;
            };
            '''))

        self._sourceTemplate = Template(shiftText('''
            #include "${Class}${HeaderSuffix}"

            struct $Class::_Implementation {
                /* DEFINE THE BODY OF THE $Class HANDLE */
            };

            $Class::$Class() : _impl(new _Implementation) {}

            $Class::~$Class() {}
            '''))


    def writeFiles(self, clsname, headerSuffix, sourceSuffix):
        headerSuffix, sourceSuffix = map(normalizeSuffix, (headerSuffix,
                                                           sourceSuffix))
        self._writeFile(self._headerTemplate, clsname, headerSuffix)
        self._writeFile(self._sourceTemplate, clsname, sourceSuffix,
                        HeaderSuffix=headerSuffix)

    def _writeFile(self, template, clsname, suffix, **kwds):
        f = file('%s%s' % (clsname, suffix), 'w')
        try:
            print >> f, template.substitute(clsname, Class=clsname, **kwds)
        finally:
            f.close()

    #def _tmpl_hdr_includes(self):
    #    return ''
    #
    #def _tmpl_hdr_inherits(self):
    #    return ''
    #
    #def _tmpl_hdr_public(self):
    #    return ''
    #
    #def _tmpl_hdr_private(self):
    #    return ''



def normalizeSuffix(suffix):
    if suffix and not suffix.startswith('.'):
        suffix = '.' + suffix
    return suffix

def shiftText(text, indent=0):
    try: space_re = shiftText.space_re
    except AttributeError:
        space_re = shiftText.space_re = re.compile(r'^\s*')
    min_indent = min(len(space_re.match(line).group())
                     for line in iterlines(text) if line) - indent
    if min_indent > 0:
        text = _nl.join(line[min_indent:] for line in iterlines(text))
    elif min_indent < 0:
        extra_pad = -min_indent * ' '
        text = _nl.join(extra_pad+line for line in iterlines(text))
    return text

def iterlines(text):
    start = 0
    len_nl = len(_nl)
    while True:
        end = text.find(_nl,start)
        if end >= 0:
            yield text[start:end]
            start = end+len_nl
        else:
            break
    if start < len(text):
        yield text[start:]



_nl = os.linesep

if __name__ == '__main__':
    def test_iterlines():
        for text in [
            #'this is one line',
            #'this is one line\nsecond line',
            'these are two lines\n',
            '\nthese are three lines\n',
            '\n',
            '']:
            assert list(iterlines(text)) == text.splitlines()
    main()
