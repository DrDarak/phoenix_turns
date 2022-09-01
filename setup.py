import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
# "packages": ["os"] is used as example only
build_exe_options = {"excludes": ["tkinter"], # need to exclude a lot
                      "include_msvcr": True,
                     'include_files':['phoenix_32x32.png',
                                      'phoenix.ico',
                                      'colour_scheme.json',
                                      'LICENSE',
                                      'phoenix.js',
                                      'tick.png',
                                      'main.css',
                                      'tree.css',
                                      'tree.js',
                                      'turns.css',
                                      'images'
                                      ],
                      'build_exe': './app',
                     }


base='Win32GUI'
setup(
    name="Phoenix_Turns",
    version="0.3",
    description="Phoenix BSE Turn Downloader",
    options={"build_exe":  build_exe_options},
    executables=[Executable("main.py",
                           base="Win32GUI",
                           icon="phoenix.ico",
                           target_name='phoenix_turns.exe',
                           copyright="Copyright (C) 2022 Skeletal Software Ltd.",
                           )],
)