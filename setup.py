#!/usr/bin/env python3
# -*- encoding:utf-8 -*-

import os
import sys
import glob

from subprocess import call
from distutils.core import setup, Extension
from distutils.command import install_scripts, install_data

import sipdistutils
import PyQt5
import pkgconfig

from rsteditor import __app_name__
from rsteditor import __app_version__

build_ext_base = sipdistutils.build_ext

pkgs = pkgconfig.parse('Qt5Widgets Qt5Gui Qt5Core')
pkgs['include_dirs'].add('rsteditor/scilexer')
pkgs['libraries'].add('qt5scintilla2')
pkg_cfg = {}
for k, v in pkgs.items():
    pkg_cfg[k] = [x for x in v]


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
        self.sip_opts += sip_flags.split(' ')
        default_sip = os.path.join(self._sip_sipfiles_dir(), 'PyQt5')
        self.sip_opts += ['-I%s' % default_sip]


class post_install_scripts(install_scripts.install_scripts):
    """ remove script ext """
    def run(self):
        install_scripts.install_scripts.run(self)
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
    platforms=['noarch'],
    packages=[
        'rsteditor',
        'rsteditor.scilexer',
    ],
    package_dir={'rsteditor': 'rsteditor'},
    data_files=[
        ('share/%s' % __app_name__.lower(), [
            'README.rst',
            'MANIFEST.in',
            'rst.properties',
        ]),
        ('share/applications', ['rsteditor.desktop']),
        ('share/pixmaps', glob.glob('pixmaps/*.*')),
        ('share/%s/template' % __app_name__.lower(), glob.glob('template/*.*')),
        ('share/%s/themes' % __app_name__.lower(), glob.glob('themes/*.*')),
        ('share/%s/docs' % __app_name__.lower(), glob.glob('docs/*.rst')),
        ('share/%s/docs/images' % __app_name__.lower(), glob.glob('docs/images/*')),
    ],
    scripts=['rsteditor.py'],
    ext_modules=[
        Extension(
            "rsteditor.scilexer.scilexerrest",
            [
                "rsteditor/scilexer/scilexerrest.sip",
                "rsteditor/scilexer/scilexerrest.cpp"
            ],
            **pkg_cfg
        ),
    ],
    cmdclass={
        'install_scripts': post_install_scripts,
        'install_data': post_install_data,
        'build_ext': my_build_ext,
    },
)
