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

root = os.path.abspath(os.path.dirname(__file__))
libraries = ["skia", "gw"]
library_dirs = [numpy.get_include(), glob.glob("./_gw/lib/skia/out/Release*")[0], "./_gw/libgw"]
include_dirs = [numpy.get_include(), ".", root, "./_gw/libgw/include", "./_gw/lib/skia", "./_gw/lib/libBigWig"]
extra_objects = glob.glob("./gwplot/libgw.*")
print("Libs", libraries)
print("Library dirs", library_dirs)
print("Include dirs", include_dirs)
print("Extra objects", extra_objects)

ret = run(f"cd _gw; make shared; cp -rf libgw ..",
# ret = run(f"cd _gw; make clean; make prep; make shared; cp -rf libgw ..",
          shell=True)

##################
# bindings build #
##################
m_ext_module = cythonize(Extension("gwplot.interface",
                            ["gwplot/interface.pyx"],
                                    libraries=libraries,
                                    library_dirs=library_dirs,
                                    include_dirs=include_dirs,
                                    extra_compile_args=extras_args,
                                    # runtime_library_dirs=["./gwplot"],
                                    language="c++",
                                    extra_objects=extra_objects,
                                    ), **cy_options)


shared = glob.glob(f"{root}/build/lib*/gwplot/*.so") + glob.glob(f"{root}/build/lib*/gwplot/*.dll")
[shutil.copy(i, f"{root}/gwplot") for i in shared]
print("Shared: ", shared)

###################
# Basic build_ext #
###################
class build_py(_build_py):
    def run(self):
        if len(glob.glob("./gwplot/libgw.*")) == 0 or "REBUILD_GW" in os.environ:
            if ret.returncode != 0:
                print("Unable to build gw")
                print(ret)
                exit(ret.returncode)
        else:
            print("[INFO] GW already built, to re-build add REBUILD_GW=1 as environment variable", file=sys.stderr)
        self.run_command("build_ext")
        return super().run()

    def initialize_options(self):
        super().initialize_options()
        if self.distribution.ext_modules == None:
            self.distribution.ext_modules = []

        self.distribution.ext_modules.extend(
            m_ext_module
        )