import os
import glob
import shutil
import sysconfig
import setuptools
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

##################
# WFA2_lib build #
##################
extras = ["-Wno-unused-function", "-Wno-unused-result",
          "-Wno-ignored-qualifiers", "-Wno-deprecated-declarations"]
extras_pywfa = get_extra_args(extras)

root = os.path.abspath(os.path.dirname(__file__))
gw = os.path.join(root, "gw")
libraries = ["gw"]
library_dirs = [f"{gw}/libgw"]
include_dirs = [".", root, gw, f"gw/libgw/include"]

print("Libs", libraries)
print("Library dirs", library_dirs)
print("Include dirs", include_dirs)


ret = run(f"cd gw; make clean; make prep; make shared",
          shell=True)
if ret.returncode != 0:
    print("Unable to build gw")
    print(ret)
    exit(ret.returncode)

##################
# bindings build #
##################
m_ext_module = cythonize(Extension("libgw.interface",
                                ["libgw/interface.pyx"],
                                libraries=libraries,
                                library_dirs=library_dirs,
                                include_dirs=include_dirs,
                                extra_compile_args=extras_pywfa,
                                language="c",
                                extra_objects=[f"{gw}/lib/libwfa.a"]
                                ),
                        **cy_options)

shared = glob.glob(f"{root}/build/lib*/libgw/*.so") + glob.glob(f"{root}/build/lib*/libgw/*.dll")
[shutil.copy(i, f"{root}/libgw") for i in shared]

###################
# Basic build_ext #
###################
# Thanks to https://stackoverflow.com/questions/73800736/pyproject-toml-and-cython-extension-module
class build_py(_build_py):
    def run(self):
        self.run_command("build_ext")
        return super().run()

    def initialize_options(self):
        super().initialize_options()
        if self.distribution.ext_modules == None:
            self.distribution.ext_modules = []

        self.distribution.ext_modules.extend(
            m_ext_module
        )