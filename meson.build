project('gwplot', 'c', 'cpp', 'cython',
  default_options: [
    'buildtype=release',
    'warning_level=1',
    'cpp_std=c++17',
  ],
  meson_version: '>=1.1.0'
)


# Python
# -----------------------------------------------------------------------------
py = import('python').find_installation(pure: false)
py_dep = py.dependency()


# System / environment detection
# -----------------------------------------------------------------------------
system   = host_machine.system()
old_skia = get_option('old_skia')
build_env = environment()
build_env.set('MESON_SOURCE_ROOT', meson.current_source_dir())
build_env.set('MESON_BUILD_ROOT',  meson.current_build_dir())
build_env.set('OLD_SKIA',          old_skia.to_string())


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


# Build libgw library via custom target
# -----------------------------------------------------------------------------
build_gw_py = files('build_gw.py')

lib_build = custom_target(
  'build_gw',
  output  : [libgw_filename, 'libskia.a'],
  command : [ py, build_gw_py, '@OUTPUT0@', '@OUTPUT1@'],
  env              : build_env,
  build_by_default : true,
  install          : true,
  install_dir      : py.get_install_dir() / 'gwplot',
)

libgw_target   = lib_build               # first output is the shared lib
libgw_path     = lib_build[0]            # File() object for libgw.* in build dir
libskia_target = lib_build               # same custom_target (second output)
libskia_path   = lib_build[1]            # File() object for libskia.a


# Python header dependencies
# -----------------------------------------------------------------------------
numpy_dep = dependency('numpy')

pysam_inc_cmd = run_command(py, ['-c', 'import pysam, sys; print(":".join(pysam.get_include() if isinstance(pysam.get_include(), list) else [pysam.get_include()]))'], check : true)
pysam_inc_dirs = []
foreach inc : pysam_inc_cmd.stdout().strip().split(':')
  if inc != ''
    pysam_inc_dirs += include_directories(inc, is_system: true)
  endif
endforeach


# Extra include/lib search prefixes for Homebrew / conda
# -----------------------------------------------------------------------------
custom_prefix = get_option('prefix_path')

if custom_prefix != ''
  sys_prefix = custom_prefix
else
  prefix_candidates = [
    '/opt/homebrew',
    '/usr/local',
    run_command('sh', ['-c', 'echo $CONDA_PREFIX'], check: false).stdout().strip(),
    run_command('sh', ['-c', 'echo $PREFIX'], check: false).stdout().strip(),
  ]
  sys_prefix = ''
  foreach candidate : prefix_candidates
    if candidate != '' and fs.exists(candidate)
      sys_prefix = candidate
      break
    endif
  endforeach
endif

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

# Note: We'll handle Skia and libgw linking through the extension module sources
# instead of link_args to avoid path resolution issues

rpath_dirs = system == 'darwin' ? ['@loader_path', '@loader_path/.'] : ['$ORIGIN', '$ORIGIN/.']


# GLFW
# -----------------------------------------------------------------------------
glfw_dep = dependency(['glfw3', 'glfw'], required : false)
if not glfw_dep.found()
  cc = meson.get_compiler('c')
  if cc.find_library('glfw3', required : false).found()
    link_args += ['-lglfw3']
  elif cc.find_library('glfw', required : false).found()
    link_args += ['-lglfw']
  else
    error('GLFW library not found. Please install glfw3 or glfw development packages.')
  endif
endif


# libgw dependency object
# -----------------------------------------------------------------------------
gw_inc = [
  include_directories('gw/libgw'),
  include_directories('gw/libgw/GW'),
]
# Don't use libgw_path.full_path() here since the file doesn't exist yet
# Instead, we'll handle the linking through the extension module sources
libgw_dep = declare_dependency(
  include_directories: gw_inc,
  dependencies       : [glfw_dep],
)


# Cython
# -----------------------------------------------------------------------------
cython = find_program('cython3', 'cython', required: true)


# gwplot extension modules
# -----------------------------------------------------------------------------
inc_dirs = include_directories('gwplot')

foreach ext : ['glfw_interface', 'interface']
  pyx_src = files('gwplot' / ext + '.pyx')

  gen_cpp = custom_target(
    ext + '_cpp',
    input  : pyx_src,
    output : ext + '.cpp',
    command: [cython, '-3', '--cplus', '@INPUT@', '-o', '@OUTPUT@'],
    depends: lib_build,
  )

py.extension_module(
    ext,
    gen_cpp,                                # C++ generated by Cython
    libgw_path,                             # Add the libgw dylib as a source (this ensures dependency and linking)
    libskia_path,                           # Add libskia.a as a source (this ensures dependency and linking)

    dependencies       : [py_dep, numpy_dep, libgw_dep, glfw_dep],

    include_directories: [inc_dirs]
                          + pysam_inc_dirs
                          + gw_inc
                          + extra_inc_dirs,
    cpp_args           : cpp_args,
    link_args          : link_args,         # Just the basic link args without the custom libraries
    install            : true,
    install_rpath      : ':'.join(rpath_dirs),
    build_rpath        : meson.current_build_dir(),
    subdir             : 'gwplot',
  )
endforeach



# Install pure-Python bits
# -----------------------------------------------------------------------------
py.install_sources('gwplot/__init__.py', subdir: 'gwplot')
foreach pxd : ['gwplot/interface.pxd', 'gwplot/glfw_interface.pxd']
  if fs.exists(pxd)
    py.install_sources(pxd, subdir: 'gwplot')
  endif
endforeach


# Runtime libraries
# -----------------------------------------------------------------------------
#install_data(libgw_path,
#             install_dir: py.get_install_dir() / 'gwplot')

#install_data(gw_lib_dir / 'libskia.a',
#             install_dir: py.get_install_dir() / 'gwplot')