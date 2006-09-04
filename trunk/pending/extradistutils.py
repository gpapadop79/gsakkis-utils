'''Extension utilities of the distutils package.'''

import sys, os
from distutils.core import Extension
from distutils.command.build import build
from distutils import log
if sys.version_info[:2] < (2,4):
    from build_ext_24 import build_ext
else:
    from distutils.command.build_ext import build_ext


__author__ = "George Sakkis <gsakkis@rutgers.edu>"
__all__ = ["AutoIncludeExtension", "BuildNoSwig",
           "BuildExtension", "BuildExtensionNoSwig"]


class AutoIncludeExtension(Extension):
    '''
    An Extension that adds automatically in include_dirs the directories
    of all source files.
    '''
    def __init__(self, name, sources, **kwds):
        Extension.__init__(self,name,sources,**kwds)
        if not hasattr(self, 'swig_opts'): # distutils < 2.4
            self.swig_opts = []
        dirs = self.include_dirs
        for source in sources:
            dir = os.path.dirname(source)
            if dir not in dirs:
                dirs.insert(0,dir)


class BuildExtension(build_ext):
    '''A swig-friendly build_ext extension (no pun intended).

    The differences of this class to build_ext in how swig files are processed
    are the following:
        - It adds a '-I' (include) swig option for each directory that
        contains a source file in the given Extension.
        - Determines whether to add the '-c++" option by checking the source
        file extensions (even if the 'swig_cpp' and 'swig_opts' do not
        explicitly specify that the extension is a c++ wrapper).
        - Builds the swig-generated high-level python module (build_ext builds
        only the low level '.dll' or '.so' file).
    '''
    # XXX: Implementation adapted from latest distutils (python2.4)

    def swig_sources (self, sources, extension):
        """Walk the list of source files in 'sources', looking for SWIG
        interface (.i) files.  Run SWIG on all that are found, and
        return a modified 'sources' list with SWIG source files replaced
        by the generated C (or C++) files.
        """
        is_cpp = self._is_cpp(sources)
        # get the source->target mapping and the new sources
        swig_targets,new_sources = self._get_swig_targets(sources,is_cpp)
        if not swig_targets:
            return sources
        # form the swig command
        swig = self.swig or self.find_swig()
        swig_cmd = [swig, "-python"]
        swig_cmd.extend(self.swig_opts)
        if is_cpp:
            swig_cmd.append("-c++")
        # Do not override commandline arguments
        if not self.swig_opts:
            for o in extension.swig_opts:
                swig_cmd.append(o)
        # add swig include dirs
        for dir in extension.include_dirs:
            option = "-I%s" % dir
            if option not in swig_cmd:
                swig_cmd.append(option)
        # invoke swig
        swig_sources = swig_targets.keys()
        for source in swig_sources:
            target = swig_targets[source]
            log.info("swigging %s to %s", source, target)
            self.spawn(swig_cmd + ["-o", target, source])
        # build (i.e. copy) the generated python modules
        self._build_swig_gen_pymodules(swig_sources, extension)
        return new_sources

    def _get_swig_targets(self, sources, is_cpp):
        '''Map the C/C++/swig sources to the new sources after swig files are
        processed.

        @return: (swig_targets,new_sources) where swig_targets is a dictionary
        from each swig target to the respective C/C++ wrapper and new_sources
        is the list of the new sources to be built.
        '''
        new_sources = []
        swig_targets = {}
        target_ext = is_cpp and '.cpp' or '.c'
        for source in sources:
            (base, ext) = os.path.splitext(source)
            if ext == ".i":             # SWIG interface file
                new_sources.append(base + '_wrap' + target_ext)
                swig_targets[source] = new_sources[-1]
            else:
                new_sources.append(source)
        return swig_targets, new_sources

    def _build_swig_gen_pymodules(self, swig_sources, extension):
        """Build the swig-generated python modules."""
        # get the extensions package
        try:
            last_dot_index = extension.name.rindex('.') + 1
            package = extension.name[:last_dot_index]
        except ValueError:
            package = ""
        modules = []
        for source in swig_sources:
            base = os.path.basename(source)
            modules.append(package + os.path.splitext(base)[0])
        build_py_cmd = self.get_finalized_command('build_py')
        build_py_cmd.py_modules = modules
        build_py_cmd.run()

    def _is_cpp(self, sources):
        """Determine if a C++ extension is to be built."""
        if self.swig_cpp:
            log.warn("--swig-cpp is deprecated - use --swig-opts=-c++")
        if self.swig_cpp or ('-c++' in self.swig_opts):
            return 1
        detect_lang = self.compiler.detect_language
        for source in sources:
            if detect_lang(source) == "c++":
                return 1
        return 0


class BuildExtensionNoSwig(BuildExtension):
    """Build an extension module assuming that any swig input files have
    been processed by swig and the associated wrappers have been generated.

    Specifically, for each (module).i file encountered in the extension's
    sources, two generated wrappers are expected to be present - the
    high-level (module).py and the low-level (module).c or (module).cpp,
    depending on whether it's a C or C++ wrapper.
    """
    def swig_sources(self, sources, extension=None):
        target_ext = self._is_cpp(sources) and '.cpp' or '.c'
        new_sources,swig_sources = [], []
        for source in sources:
            (base, ext) = os.path.splitext(source)
            if ext == ".i":             # SWIG interface file
                new_sources.append(base + '_wrap' + target_ext)
                swig_sources.append(source)
            else:
                new_sources.append(source)
        # build the swig-generated python modules
        self._build_swig_gen_pymodules(swig_sources, extension)
        return new_sources


class BuildNoSwig(build):
    """A build subclass with BuildExtensionNoSwig as subcommand in the place
    of build_ext.
    """
    #sub_commands = _replaceSubcommands(build.sub_commands,
    #                                   build_ext='build_ext_no_swig')
    sub_commands = list(build.sub_commands)
    for index in xrange(len(sub_commands)):
        cmd_name, method = sub_commands[index]
        if cmd_name == 'build_ext':
            sub_commands[index] = ('build_ext_no_swig', method)
            break


#def _replaceSubcommands(sub_commands, **old2new):
#    new_sub_commands = list(sub_commands)
#    for index in xrange(len(new_sub_commands)):
#        cmd_name, method = new_sub_commands[index]
#        try: new_sub_commands[index] = (old2new[cmd_name], method)
#        except KeyError: pass
#    return new_sub_commands
