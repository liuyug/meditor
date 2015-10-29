#!/usr/bin/env python
# -*- encoding:utf-8 -*-
# python setup_cxFreeze.py build -c mingw32

import os
import sys
import glob

from subprocess import call
from cx_Freeze import setup, Executable
from distutils.core import Extension
from distutils.command import install_scripts, install_data

import PyQt5
import sipdistutils


build_ext_base = sipdistutils.build_ext
pyqt_path = os.path.dirname(PyQt5.__file__)
qt_path = 'C:\\Qt\\Qt5.5.1\\5.5\\mingw492_32'

from rsteditor import __app_name__
from rsteditor import __app_version__

options = {}
build_exe_options = {
    'packages': [
    ],
    'includes': [
        'rsteditor',
    ],
    'include_files': [
        (os.path.join('build', 'lib.win32-3.4', 'rsteditor', 'scilexerrest.pyd'),
         os.path.join('rsteditor', 'scilexerrest.pyd')),
    ],
}
base = None

if sys.platform == "win32":
    base = "Win32GUI"
    base = None
    options['build_exe'] = build_exe_options

execute_scripts = [
    Executable(script='rsteditor.py', icon='pixmaps/rsteditor-text-editor.ico', base=base)
]


class my_build_ext(build_ext_base):
    def run(self):
        try:
            build_ext_base.run(self)
        except Exception as err:
            print('Compile PyQt extension error: %s.' % err)
            print('Use PYTHON rst lexer.')

    def finalize_options(self):
        build_ext_base.finalize_options(self)
        from PyQt5.QtCore import PYQT_CONFIGURATION
        sip_flags = PYQT_CONFIGURATION.get('sip_flags', '')
        pyqt_sip = os.path.join(pyqt_path, 'sip', 'PyQt5')
        self.sip_opts += sip_flags.split(' ')
        self.sip_opts += ['-I%s' % pyqt_sip]


class post_install_scripts(install_scripts.install_scripts):
    """ remove script ext """
    def run(self):
        install_scripts.install_scripts.run(self)
        return
        if sys.platform == 'win32':
            for script in self.get_outputs():
                if script.endswith(".py"):
                    new_name = '%s_gui.py' % script[:-3]
                    if os.path.exists(new_name):
                        os.remove(new_name)
                    print('renaming %s -> %s' % (script, new_name))
                    os.rename(script, new_name)
        else:
            for script in self.get_outputs():
                if script.endswith(".py"):
                    new_name = script[:-3]
                    if os.path.exists(new_name):
                        os.remove(new_name)
                    print('renaming %s -> %s' % (script, new_name))
                    os.rename(script, new_name)
        return


class post_install_data(install_data.install_data):
    """ update desktop """
    def run(self):
        install_data.install_data.run(self)
        return
        if sys.platform == 'win32':
            dist_path = os.path.join(
                os.path.realpath(os.path.dirname(__file__)),
                'dist')
            import docutils
            import shutil
            docutils_path = os.path.dirname(docutils.__file__)
            rst_writer_path = os.path.join(dist_path, 'docutils', 'writers')
            if os.path.exists(rst_writer_path):
                shutil.rmtree(rst_writer_path)
            shutil.copytree(os.path.join(docutils_path, 'writers'),
                            rst_writer_path,
                            ignore=shutil.ignore_patterns('*.py'))
            if os.path.exists(os.path.join(dist_path, 'imageformats')):
                shutil.rmtree(os.path.join(dist_path, 'imageformats'))
            shutil.copytree(
                os.path.join(pyqt_path, 'plugins', 'imageformats'),
                os.path.join(dist_path, 'imageformats')
            )
        else:
            print('running update-desktop-database')
            call('update-desktop-database')


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
    # platforms=['noarch'],
    # packages=['rsteditor'],
    # package_dir={'rsteditor': 'rsteditor'},
    # data_files=[
    #     ('share/%s' % __app_name__.lower(), [
    #         'README.rst',
    #         'MANIFEST.in',
    #         'rst.properties',
    #     ]),
    #     ('share/applications', ['rsteditor.desktop']),
    #     ('share/pixmaps', glob.glob('pixmaps/*.*')),
    #     ('share/%s/template' % __app_name__.lower(), glob.glob('template/*.*')),
    #     ('share/%s/themes' % __app_name__.lower(), glob.glob('themes/*.*')),
    #     ('share/%s/docs' % __app_name__.lower(), glob.glob('docs/*.rst')),
    #     ('share/%s/docs/images' % __app_name__.lower(), glob.glob('docs/images/*')),
    # ],
    cmdclass={
        # 'install_scripts': post_install_scripts,
        # 'install_data': post_install_data,
        'build_ext': my_build_ext,
    },
    ext_modules=[
        Extension(
            "rsteditor.scilexerrest",
            [
                "rsteditor/scilexerrest.sip",
                "rsteditor/scilexerrest.cpp"
            ],
            include_dirs=[
                '/usr/include/qt5',
                '/usr/include/qt5/QtCore',
                '/usr/include/qt5/QtGui',
                '/usr/include/qt5/QtWidgets',
                os.path.join(pyqt_path, 'include'),
                os.path.join(qt_path, 'include'),
                os.path.join(qt_path, 'include', 'QtCore'),
                os.path.join(qt_path, 'include', 'QtGui'),
                os.path.join(qt_path, 'include', 'QtWidgets'),
                'rsteditor',
            ],
            library_dirs=[
                os.path.join(qt_path, 'lib'),
            ],
            libraries=['qscintilla2', 'Qt5Core', 'Qt5Gui', 'Qt5Widgets'],
        ),
    ],
    options=options,
    executables=execute_scripts,
)
