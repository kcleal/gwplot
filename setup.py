from setuptools import setup, find_packages
import setuptools
from setuptools.extension import Extension
from setuptools.command.build_ext import build_ext
from Cython.Build import cythonize
import numpy
from distutils import ccompiler
import os
import sysconfig
import platform
import subprocess
import shutil


def get_system_prefix():
    if shutil.which('brew'):
        try:
            result = subprocess.run(['brew', '--prefix'],
                                    capture_output=True,
                                    text=True,
                                    check=True)
            if result.stdout.strip():
                return result.stdout.strip()
        except subprocess.CalledProcessError:
            pass

    conda_prefix = os.environ.get('CONDA_PREFIX')
    if conda_prefix:
        return conda_prefix

    prefix = os.environ.get('PREFIX')
    if prefix:
        return prefix

    return None


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

old_skia = os.environ.get('OLD_SKIA') == "1"

extras = ["-Wno-unused-function", "-Wno-unused-result",
          "-Wno-ignored-qualifiers", "-Wno-deprecated-declarations"]
extras_args = (get_extra_args(extras) + os.environ.get('CXXFLAGS', '').split() +
               ["-std=c++17",
                "-DBUILDING_LIBGW",
                "-DGLAD_GLAPI_EXPORT",
                "-DGLAD_GLAPI_EXPORT_BUILD"])

if old_skia:
    extras_args += ["-DOLD_SKIA=1"]

print('CXXFLAGS:', os.environ.get('CXXFLAGS', ''))
print("Extra compile args:",  extras_args)
print("*"*80)

root = os.path.abspath(os.path.dirname(__file__))

include_dirs = [numpy.get_include(), f"{root}/gw/libgw/GW"] + os.environ.get('CPPFLAGS', '').split()
libraries = ["hts", "skia", "gw"]
library_dirs = [numpy.get_include(), f"{root}/gwplot", f"{root}/gw/libgw"] + os.environ.get('LDFLAGS', '').split()

extra_link_args = []
if os_name == 'Darwin':
    extra_link_args = ['-Wl,-rpath,@loader_path',
                       '-Wl,-rpath,@loader_path/.',
                       '-framework', 'Metal',
                       '-framework', 'OpenGL',
                       '-framework', 'AppKit',
                       '-framework', 'ApplicationServices',
                       '-framework', 'CoreText']
elif os_name == 'Linux':
    extra_link_args = [
        '-Wl,-rpath,$ORIGIN',
        '-Wl,-rpath,$ORIGIN/.'
    ]

sys_prefix = get_system_prefix()
if sys_prefix:
    print("Using system prefix:", sys_prefix)
    if os.path.exists(f"{sys_prefix}/include"):
        include_dirs.append(f"{sys_prefix}/include")
    if os.path.exists(f"{sys_prefix}/include/GW"):
        include_dirs.append(f"{sys_prefix}/include/GW")
    if os.path.exists(f"{sys_prefix}/lib"):
        library_dirs.append(f"{sys_prefix}/lib")

print("Libs", libraries)
print("Library dirs", library_dirs)
print("Include dirs", include_dirs)

ext_modules = []
for item in ("glfw_interface", "interface"):
    ext_modules.append( Extension(f"gwplot.{item}",
                            [f"gwplot/{item}.pyx"],
                                    libraries=libraries,
                                    library_dirs=library_dirs,
                                    include_dirs=include_dirs,
                                    extra_compile_args=extras_args,
                                    extra_link_args=extra_link_args,
                                    language="c++",
                                    runtime_library_dirs=[
                                            os.path.abspath("$ORIGIN"),
                                            os.path.abspath("$ORIGIN/."),
                                        ] if os_name == 'Linux' else None
                            )
                        )


ext_modules = cythonize(ext_modules, **cy_options)


class CustomBuildExt(build_ext):
    def run(self):
        # Build libgw.dylib using the Makefile and copy to the gwplot directory
        libgw_dir = os.path.join(os.getcwd(), 'gw', 'libgw')
        if not os.path.exists(f'{os.getcwd()}/gw/lib/skia'):
            if old_skia:
                subprocess.run(f'cd {os.getcwd()}/gw; OLD_SKIA=1 make prep', shell=True)
            else:
                subprocess.run(f'cd {os.getcwd()}/gw; make prep', shell=True)
        if old_skia:
            print('Building libgw (OLD_SKIA=1)')
            subprocess.run(f'cd {os.getcwd()}/gw; OLD_SKIA=1 make shared', shell=True)
        else:
            print('Building libgw')
            subprocess.run(f'cd {os.getcwd()}/gw; make shared', shell=True)
        if os_name == 'Linux':
            ext = "so"
        else:
            ext = "dylib"
        libgw_src = os.path.join(libgw_dir, f'libgw.{ext}')
        libgw_dest = os.path.join(os.getcwd(), 'gwplot', f'libgw.{ext}')
        shutil.copy(libgw_src, libgw_dest)

        super().run()

setup(
    name="gwplot",
    version="0.2.0",
    packages=find_packages(where="."),
    ext_modules=ext_modules,
    include_package_data=True,
    package_data={
        'gwplot': [
            '*.so',
            '*.pxd',
            '*.a',
            '*.dylib',
        ]
    },
    cmdclass={
        'build_ext': CustomBuildExt,  # Use the custom build command
    },
    zip_safe=False,
)
