from setuptools import setup, find_packages
from distutils import log
from collections import defaultdict
from os.path import join
import os

import apaf
from apaf import config

ICONFILE = None
APP = [os.path.join('apaf', 'main.py')]

# static files
DATA_FILES = [(root, [join(root, file) for file in files])
              for root, _, files in os.walk(join('datadir'))]

PLATFORM_OPTIONS = defaultdict(dict)

## DARWIN options. ##
if config.platform == 'darwin':
    import operator
    import py2app
    from apaf.utils.osx_support import OSXPatchCommand

    # files needed to create app Bundle on os x (icon, status bar icon ...)
    DATA_FILES = [join('datadir', 'config'), join('datadir', 'contrib'), join('datadir', 'services')]
    DATA_FILES += reduce(operator.add,
        [[join(root,file) for file in files]
         for root, _, files in os.walk(join('datadir', 'osx_bundle'))])
else:
    OSXPatchCommand = None

OPTIONS_PY2APP = dict(
    argv_emulation = True,
    iconfile = ICONFILE,
    plist={
        'LSUIElement':0, # Agent Only App (No icon in dock)
    }
#    install_requires=['py2app>=0.6.4'],
)

PLATFORM_OPTIONS['darwin'] = dict(
    cmdclass={
        'osx_patch': OSXPatchCommand
    },
)

## WINDOWS otions. ##
if config.platform == 'win32':
    from py2exe.build_exe import py2exe as _py2exe

    class py2exe(_py2exe):
        def create_binaries(self, *args, **kwargs):
            """
            Generate the blob module for static files, too.
            """
            from apaf.blobber import create_blobbone
            create_blobbone(config._datadir,
                            join(config._root_dir, 'win32blob.py'))

            _py2exe.create_binaries(self, *args, **kwargs)

PLATFORM_OPTIONS['win32'] = dict(
    zipfile = None,
    console = APP,
#    windows = APP,    # run as window, not console application.
)

OPTIONS_PY2EXE = dict(
    bundle_files = 1,
    compressed = True,
    optimize = 2,
#   install_requires=['py2exe>=0.6.9', 'pywin32'],
)

## linux options ##
if config.platform == 'linux2':
    DATA_FILES = [(join('share', config.appname, dest), source)
                  for dest, source in DATA_FILES]

setup(
    name=config.appname,
    description=config.description,
    version=apaf.__version__,
    author=apaf.__author__,
    author_email=apaf.__email__,
    url=apaf.__url__,
    app=APP,
    data_files=DATA_FILES,
    options=dict(py2app=OPTIONS_PY2APP,
                 py2exe=OPTIONS_PY2EXE,
    ),
    entry_points=dict(console_scripts=['apaf = apaf.main']),
    packages=find_packages(exclude=['test']),
    **PLATFORM_OPTIONS[config.platform]
)
