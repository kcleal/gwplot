import os
import sys
import glob
import shutil
import sysconfig
import setuptools
import numpy
from subprocess import run
from distutils import ccompiler
from setuptools import Extension
from Cython.Build import cythonize
from setuptools.command.build_py import build_py as _build_py

###########
# Helpers #
###########
debug = False

cy_options = {
    'annotate': False,
    'compiler_directives': {
        'profile': debug,
        'linetrace': debug,
        'boundscheck': debug,
        'wraparound': debug,
        'nonecheck': debug,
        'initializedcheck': debug,
        'language_level': 3
    }
}

cfg_vars = sysconfig.get_config_vars()
for key, value in cfg_vars.items():
    if type(value) == str:
        cfg_vars[key] = value.replace("-Wstrict-prototypes", "")

def has_flag(compiler, flagname):
    """Return a boolean indicating whether a flag name is supported on
    the specified compiler.
    """
    import tempfile
    with tempfile.NamedTemporaryFile('w', suffix='.c') as f:
        f.write('int main (int argc, char **argv) { return 0; }')
        try:
            compiler.compile([f.name], extra_postargs=[flagname])
        except setuptools.distutils.errors.CompileError:
            return False
    return True

def get_extra_args(flags):
    compiler = ccompiler.new_compiler()
    extra_compile_args = []
    for f in flags:
        if has_flag(compiler, f):
            extra_compile_args.append(f)
    return extra_compile_args

###############
# gwplot build #
###############
extras = ["-Wno-unused-function", "-Wno-unused-result",
          "-Wno-ignored-qualifiers", "-Wno-deprecated-declarations"]
extras_args = get_extra_args(extras) + ["-std=c++17"]

print("Extra compile args:",  extras_args)
print("*"*80)

if os.getenv('SKIP_PREP') is not None:
    ret = run(f"cd gw; make shared; cp -rf libgw/include ../; cp libgw.* ../gwplot", shell=True)
else:
    ret = run(f"cd gw; make prep; make shared; cp -rf libgw/include ../; cp libgw.* ../gwplot", shell=True)

# ret = run(f"cd gw; make clean; make prep; make shared; cp -rf libgw ..", shell=True)
if ret.returncode != 0:
    print("Unable to build gw")
    print(ret)
    exit(ret.returncode)


root = os.path.abspath(os.path.dirname(__file__))
libraries = ["skia", "gw"]

library_dirs = [numpy.get_include(), glob.glob("./gw/lib/skia/out/Release*")[0], "./gwplot"]
include_dirs = [numpy.get_include(), "./include", "./gw/lib/skia", "./gw/lib/libBigWig", "./gw/src"]
print("Libs", libraries)
print("Library dirs", library_dirs)
print("Include dirs", include_dirs)

link_args = []
if sys.platform == "darwin":
    link_args = ["-Wl,-rpath,@loader_path", "-lhts", "-Wl,-rpath,@loader_path", "-lgw"]
else:
    link_args = ["-Wl,-rpath,$ORIGIN", "-lhts", "-Wl,-rpath,$ORIGIN", "-lgw"]
##################
# bindings build #
##################
m_ext_module = cythonize(Extension("gwplot.interface",
                        ["gwplot/interface.pyx"],
                                libraries=libraries,
                                library_dirs=library_dirs,
                                include_dirs=include_dirs,
                                extra_compile_args=extras_args,
                                language="c++",
                                # extra_link_args=link_args,
                                    ), **cy_options)


###################
# Basic build_ext #
###################
class build_py(_build_py):
    def run(self):
        self.run_command("build_ext")
        dest = f"{root}/build/lib/gwplot"
        if sys.platform == "darwin":  # Fix rpath
            run(f"otool -L {dest}/interface.cpython-310-darwin.so", shell=True)
            run(f"install_name_tool -change libgw.so @loader_path/libgw.so {dest}/interface.cpython-310-darwin.so", shell=True)
        else:
            run("readelf -d {dest}/interface.cpython-310-linux-gnu.so", shell=True)
            run("patchelf --replace-needed libgw.so $ORIGIN/libgw.so {dest}/interface.cpython-310-linux-gnu.so", shell=True)
        # Copy .so just for unit tests
        source = glob.glob(f'{dest}/interface.cpyth*.so')[0]
        destination = f'{root}/gwplot/'
        shutil.copy(source, destination)

        return super().run()

    def initialize_options(self):
        super().initialize_options()
        if self.distribution.ext_modules == None:
            self.distribution.ext_modules = []

        self.distribution.ext_modules.extend(
            m_ext_module
        )