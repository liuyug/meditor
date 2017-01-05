#!/usr/bin/env python
# -*- encoding:utf-8 -*-
# tip:
#   pyqt 5.5.1 is compiled with msvc 2010
#   to build extention it need to install qt-5.5.1 with msvc2010
# python setup_cxFreeze.py build

import os
import sys

from cx_Freeze import setup, Executable
from distutils.core import Extension
from distutils.command import install_data

import sipdistutils
import sipconfig
import docutils
import PyQt5

from rsteditor import __app_name__
from rsteditor import __app_version__
from rsteditor.util import get_include_files


build_ext_base = sipdistutils.build_ext
install_data_base = install_data.install_data

sip_cfg = sipconfig.Configuration()
if sip_cfg.platform == 'win32-msvc2010':
    qt_path = 'C:\\Qt\\Qt5.5.1.msvc2010\\5.5\\msvc2010'
elif sip_cfg.platform == 'win32-g++':
    qt_path = 'C:\\Qt\\Qt5.5.1.mingw\\5.5\\mingw492_32'
else:
    qt_path = '/usr/include'
pyqt_path = os.path.dirname(PyQt5.__file__)
docutils_path = os.path.dirname(docutils.__file__)

include_files = []
include_files += get_include_files(
    docutils_path,
    ['*.css', '*.txt', '*.tex', '*.odt', '__base__'],
    'docutils'
)

include_files.append(['README.rst', 'README.rst'])
include_files.append(['rst.properties', 'rst.properties'])
include_files.append(['MANIFEST.in', 'MANIFEST.in'])
include_files.append(['rsteditor.desktop', 'applications/rsteditor.desktop'])
include_files += get_include_files('pixmaps', ['*.*'], 'pixmaps')
include_files += get_include_files('template', ['skeleton.*'], 'template')
include_files += get_include_files('docs', ['*.rst', '*.png'], 'docs')
include_files += get_include_files('themes', ['*.css', '*.json'], 'themes')

zip_includes = []

build_exe_options = {
    'packages': [
        'pygments',
        'docutils',
    ],
    'includes': [
    ],
    'excludes': [
        'unittest',
    ],
}

build_exe_options['include_files'] = include_files
build_exe_options['zip_includes'] = zip_includes

base = None

options = {}
if sys.platform == "win32":
    base = "Win32GUI"
    options['build_exe'] = build_exe_options

execute_scripts = [
    Executable(script='rsteditor.py', icon='pixmaps/rsteditor-text-editor.ico', base=base)
]


class my_build_ext(build_ext_base):
    def run(self):
        try:
            build_ext_base.run(self)
            global include_files
            include_files += get_include_files(
                os.path.realpath(self.build_lib),
                ['*.pyd'],
                '',
            )
        except Exception as err:
            print('Compile PyQt extension error: %s.' % err)
            print('Use PYTHON rst lexer.')

    def finalize_options(self):
        build_ext_base.finalize_options(self)
        from PyQt5.QtCore import PYQT_CONFIGURATION
        sip_flags = PYQT_CONFIGURATION.get('sip_flags', '')
        self.sip_opts += sip_flags.split(' ')
        pyqt_sip = os.path.join(pyqt_path, 'sip', 'PyQt5')
        self.sip_opts += ['-I%s' % pyqt_sip]
        default_sip = os.path.join(self._sip_sipfiles_dir(), 'PyQt5')
        self.sip_opts += ['-I%s' % default_sip]


with open('README.rst') as f:
    long_description = f.read()

setup(
    name=__app_name__.lower(),
    version=__app_version__,
    author='Yugang LIU',
    author_email='liuyug@gmail.com',
    url='https://github.com/liuyug/rsteditor-qt.git',
    license='GPLv3',
    description='Editor for ReStructedText',
    long_description=long_description,
    cmdclass={
        'build_ext': my_build_ext,
    },
    ext_modules=[
        Extension(
            "rsteditor.scilexer.scilexerrest",
            [
                "rsteditor/scilexer/scilexerrest.sip",
                "rsteditor/scilexer/scilexerrest.cpp"
            ],
            include_dirs=[
                'rsteditor/scilexer',
                os.path.join(qt_path, 'include'),
                os.path.join(qt_path, 'include', 'QtCore'),
                os.path.join(qt_path, 'include', 'QtGui'),
                os.path.join(qt_path, 'include', 'QtWidgets'),
            ],
            define_macros=[
                ('QSCINTILLA_DLL', None),   # only for window msvc
            ],
            library_dirs=[
                os.path.join(qt_path, 'lib'),
            ],
            libraries=[
                'qscintilla2',
                'Qt5PrintSupport', 'Qt5Widgets', 'Qt5Gui', 'Qt5Core',
            ],
        ),
    ],
    options=options,
    executables=execute_scripts,
)
