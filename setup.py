from setuptools import setup, find_packages
import setuptools
from setuptools.extension import Extension
from Cython.Build import cythonize
import numpy
from distutils import ccompiler
import os
import sysconfig
import platform

os_name = platform.system()
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


extras = ["-Wno-unused-function", "-Wno-unused-result",
          "-Wno-ignored-qualifiers", "-Wno-deprecated-declarations"]
extras_args = get_extra_args(extras) + ["-std=c++17"]

print("Extra compile args:",  extras_args)
print("*"*80)


root = os.path.abspath(os.path.dirname(__file__))
libraries = ["hts", "skia", "gw"]

include_dirs = [numpy.get_include(),"./gw/lib/libgw/include", "./gw/lib/skia", "./gw/lib/libBigWig"]
library_dirs = [numpy.get_include(), "./gwplot", "./gw/lib/libgw/out/"]

extra_link_args = []
if os_name == 'Darwin':
    extra_link_args.append('-Wl,-rpath,@loader_path/.')
elif os_name == 'Linux':
    extra_link_args.append('-Wl,-rpath,$ORIGIN')

print("Libs", libraries)
print("Library dirs", library_dirs)
print("Include dirs", include_dirs)

ext_module = cythonize(Extension("gwplot.interface",
                        ["gwplot/interface.pyx"],
                                libraries=libraries,
                                library_dirs=library_dirs,
                                include_dirs=include_dirs,
                                extra_compile_args=extras_args,
                                extra_link_args=extra_link_args,
                                language="c++",
                                ), **cy_options)

print("Found packages", find_packages(where="."))
setup(
    name="gwplot",
    ext_modules=cythonize(ext_module),
    include_package_data=True,
)
