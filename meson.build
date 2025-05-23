project('gwplot', 'c', 'cpp', 'cython',
  default_options: [
    'buildtype=release',
    'warning_level=1',
    'cpp_std=c++17',
  ],
  meson_version: '>=1.1.0'
)

# -----------------------------------------------------------------------------
# Python
# -----------------------------------------------------------------------------
py = import('python').find_installation(pure: false)
py_dep = py.dependency()

# -----------------------------------------------------------------------------
# System / environment detection
# -----------------------------------------------------------------------------
system   = host_machine.system()
old_skia = get_option('old_skia')

# Build-script environment variables
build_env = environment()
build_env.set('MESON_SOURCE_ROOT', meson.current_source_dir())
build_env.set('MESON_BUILD_ROOT',  meson.current_build_dir())
build_env.set('OLD_SKIA',          old_skia.to_string())

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------
fs              = import('fs')
source_root_dir = meson.current_source_dir()

gw_source_dir      = source_root_dir / 'gw'
gw_lib_dir         = gw_source_dir / 'libgw'
gw_lib_include_dir = gw_lib_dir / 'GW'

# Determine the shared-library filename for the platform
if system == 'darwin'
  libgw_filename = 'libgw.dylib'
elif system == 'linux'
  libgw_filename = 'libgw.so'
else
  libgw_filename = 'gw.dll'
endif

libgw_path = gw_lib_dir / libgw_filename

# ensure gw/libgw exists already
if not fs.exists(gw_lib_dir)
  run_command('mkdir', ['-p', gw_lib_dir], check: true)
  run_command('mkdir', ['-p', gw_lib_include_dir], check: true)
endif

# -----------------------------------------------------------------------------
# Include directories
# -----------------------------------------------------------------------------
inc_dirs = include_directories('gwplot')

gw_inc = [
  include_directories('gw/libgw'),
  include_directories('gw/libgw/GW'),
]

# -----------------------------------------------------------------------------
# Build gw library via custom target
# -----------------------------------------------------------------------------
build_gw_py = files('build_gw.py')
libgw_stamp = custom_target('build_gw',
  output: 'libgw.stamp',
  command: [py, build_gw_py],
  env: build_env,
  build_by_default: true,
)

# -----------------------------------------------------------------------------
# Dependencies
# -----------------------------------------------------------------------------
#   – Python-level deps
numpy_dep = dependency('numpy')

#   – pysam include folders
pysam_inc_cmd = run_command(py, ['-c', '''
import pysam, sys
inc = pysam.get_include()
if isinstance(inc, list):
    print(":".join(inc))
else:
    print(inc)
'''], check: true)

pysam_inc_dirs = []
foreach inc : pysam_inc_cmd.stdout().strip().split(':')
  if inc != ''
    pysam_inc_dirs += include_directories(inc, is_system: true)
  endif
endforeach

# -----------------------------------------------------------------------------
# libgw dependency object (for consumers)
# -----------------------------------------------------------------------------
libgw_dep = declare_dependency(
  link_args: ['-L' + gw_lib_dir, '-lgw', '-lskia', '-L' + gw_source_dir / 'lib/skia'],
  include_directories: gw_inc,
)

# -----------------------------------------------------------------------------
# Extra include/lib search prefixes (Homebrew, conda, …)
# -----------------------------------------------------------------------------
sys_prefix = ''
if fs.exists('/opt/homebrew')
  sys_prefix = '/opt/homebrew'
elif fs.exists('/usr/local')
  sys_prefix = '/usr/local'
endif

foreach var : ['CONDA_PREFIX', 'PREFIX']
  env_prefix = run_command('sh', ['-c', 'echo $' + var], check: false).stdout().strip()
  if env_prefix != '' and fs.exists(env_prefix)
    sys_prefix = env_prefix
    break
  endif
endforeach

extra_inc_dirs = []
extra_lib_dirs = []
if sys_prefix != ''
  if fs.exists(sys_prefix / 'include')
    extra_inc_dirs += include_directories(sys_prefix / 'include', is_system: true)
  endif
  if fs.exists(sys_prefix / 'lib')
    extra_lib_dirs += ['-L' + sys_prefix / 'lib']
  endif
endif

# -----------------------------------------------------------------------------
# Compiler / linker flags
# -----------------------------------------------------------------------------
cpp_args = [
  '-DBUILDING_LIBGW',
  '-DGLAD_GLAPI_EXPORT',
  '-DGLAD_GLAPI_EXPORT_BUILD',
  '-Wno-unused-function',
  '-Wno-unused-result',
  '-Wno-ignored-qualifiers',
  '-Wno-deprecated-declarations',
  '-Wno-macro-redefined',
  '-DSK_GL',
]
if old_skia
  cpp_args += ['-DOLD_SKIA=1']
endif

link_args = extra_lib_dirs + ['-lhts']
if system == 'darwin'
  link_args += [
    '-framework', 'Metal',
    '-framework', 'OpenGL',
    '-framework', 'AppKit',
    '-framework', 'ApplicationServices',
    '-framework', 'CoreText',
  ]
endif

# Runtime search path for libgw at import time
rpath_dirs = system == 'darwin' ? ['@loader_path', '@loader_path/.'] : ['$ORIGIN', '$ORIGIN/.']

# -----------------------------------------------------------------------------
# Cython
# -----------------------------------------------------------------------------
cython = find_program('cython3', 'cython', required: true)

# -----------------------------------------------------------------------------
# gwplot extension modules
# -----------------------------------------------------------------------------
foreach ext : ['glfw_interface', 'interface']
  pyx_file = files('gwplot' / ext + '.pyx')

  cpp_file = custom_target(
    ext + '_cpp',
    input:  pyx_file,
    output: ext + '.cpp',
    command: [cython, '-3', '--cplus', '@INPUT@', '-o', '@OUTPUT@'],
  )

  py.extension_module(ext,
    cpp_file,                    # generated C++ from Cython
    libgw_stamp,                 # order-only dependency (headers & lib)
    dependencies: [py_dep, numpy_dep, libgw_dep],
    include_directories: [inc_dirs] + pysam_inc_dirs + gw_inc + extra_inc_dirs,
    cpp_args: cpp_args,
    link_args: link_args,
    link_depends: libgw_stamp,
    install: true,
    install_rpath: ':'.join(rpath_dirs),
    build_rpath: gw_lib_dir,
    subdir: 'gwplot',
  )
endforeach

# -----------------------------------------------------------------------------
# Install pure-Python bits
# -----------------------------------------------------------------------------
py.install_sources('gwplot/__init__.py', subdir: 'gwplot')

foreach pxd : ['gwplot/interface.pxd', 'gwplot/glfw_interface.pxd']
  if fs.exists(pxd)
    py.install_sources(pxd, subdir: 'gwplot')
  endif
endforeach

# -----------------------------------------------------------------------------
# Post-install: copy the shared library next to the Python package
# -----------------------------------------------------------------------------
install_script = '''
import shutil, os
from pathlib import Path
src  = Path("@0@")
dest = Path("@1@") / "gwplot" / src.name
print(f"Installing {src} → {dest}")
dest.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(src, dest)
'''.format(libgw_path, py.get_install_dir())

meson.add_install_script('python3', '-c', install_script)
