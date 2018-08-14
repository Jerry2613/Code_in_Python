from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.

includefiles = ['icon/', 'Guid_Unique.txt']
buildOptions = dict(packages = [], excludes = [], include_files = includefiles)

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('Application.py', base=base)
]

setup(name='BIOS_Tool',
      version = '0.1',
      description = "Jerry's BIOS tool",
      options = dict(build_exe = buildOptions),
      executables = executables)
