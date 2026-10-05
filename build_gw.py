#!/usr/bin/env python3
"""Build script for gw library - called by Meson."""

import os
import subprocess
import sys
import shutil
from pathlib import Path
import multiprocessing
jobs = multiprocessing.cpu_count()


def main():
    # Get arguments from environment or command line
    source_dir = Path(os.environ.get('MESON_SOURCE_ROOT', '.')).absolute()
    build_dir = Path(os.environ.get('MESON_BUILD_ROOT', '.')).absolute()
    old_skia = os.environ.get('OLD_SKIA', '').lower() == 'true'

    gw_dir = source_dir / 'gw'
    skia_dir = gw_dir / 'lib' / 'skia'

    # The bindings target the gw 2.x API (e.g. Region::markers, ImGui)
    version_src = (gw_dir / 'src' / 'gw_version.cpp').read_text()
    gw_version = version_src.split('GW_VERSION[] = "', 1)[1].split('"', 1)[0]
    if gw_version.split('.')[0] != '2':
        print(f"Error: gwplot requires gw 2.x, but the gw submodule is version {gw_version}")
        sys.exit(1)

    # Determine library name based on platform
    import platform
    system = platform.system()
    if system == 'Darwin':
        lib_name = 'libgw.dylib'
    elif system == 'Linux':
        lib_name = 'libgw.so'
    else:
        lib_name = 'gw.dll'

    env = os.environ.copy()
    env['OLD_SKIA'] = '1' if old_skia else '0'

    if system == 'Darwin':
        imgui_export = ' -D\'IMGUI_API=__attribute__((visibility("default")))\''
        prefix = os.environ.get('GW_SYS_PREFIX', '')
        if prefix:
            env['CPPFLAGS'] = f'-isystem {prefix}/include ' + env.get('CPPFLAGS', '')
            env['LDFLAGS'] = f'-L{prefix}/lib ' + env.get('LDFLAGS', '')
            env['PKG_CONFIG_PATH'] = (f'{prefix}/lib/pkgconfig:'
                                      + env.get('PKG_CONFIG_PATH', ''))

        env['CPPFLAGS'] = env.get('CPPFLAGS', '') + imgui_export

    # Check if we need to run make prep
    if not skia_dir.exists():
        print("Running 'make prep' to fetch Skia...")
        result = subprocess.run(
            ['make', 'prep'],
            cwd=str(gw_dir),
            env=env
        )
        if result.returncode != 0:
            print("Error: Failed to run 'make prep'")
            sys.exit(1)

    # Build the library
    print("Building libgw...")

    result = subprocess.run(
        ['make', 'shared', f'-j{jobs}'],
        cwd=str(gw_dir),
        env=env
    )
    if result.returncode != 0:
        print("Error: Failed to build libgw")
        sys.exit(1)

    # Check that the library was built
    lib_path = gw_dir / 'libgw' / lib_name
    if not lib_path.exists():
        print(f"Error: Expected library not found at {lib_path}")
        sys.exit(1)

    print(f"Successfully built {lib_name}, copying to {build_dir}")

    shutil.copy(lib_path, build_dir / lib_name)
    shutil.copy(gw_dir / 'libgw/libskia.a', build_dir / 'libskia.a')

    # Create a stamp file to indicate successful build
    stamp_file = build_dir / 'libgw.stamp'
    stamp_file.touch()
    stamp_file = build_dir / 'libskia.stamp'
    stamp_file.touch()

    return 0


if __name__ == '__main__':
    sys.exit(main())
