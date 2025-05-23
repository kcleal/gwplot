#!/usr/bin/env python3
"""Build script for gw library - called by Meson."""

import os
import subprocess
import sys
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

    print(f"Successfully built {lib_name}")

    # Create a stamp file to indicate successful build
    stamp_file = build_dir / 'libgw.stamp'
    stamp_file.touch()

    return 0

if __name__ == '__main__':
    sys.exit(main())