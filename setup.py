#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import os
import sys
import glob

from subprocess import call
from distutils.core import setup, Extension
from distutils.command import install_scripts, install_data
from PyQt4 import pyqtconfig
import sipdistutils

try:
    import py2exe
except:
    pass

from rsteditor import __app_name__
from rsteditor import __app_version__


class my_build_ext(sipdistutils.build_ext):
    def _sip_compile(self, sip_bin, source, sbf):
        cfg = pyqtconfig.Configuration()
        self.spawn([sip_bin, "-I", cfg.pyqt_sip_dir] +
                   cfg.pyqt_sip_flags.split(' ') +
                   ["-c", self.build_temp, "-b", sbf, source]
                   )


class post_install_scripts(install_scripts.install_scripts):
    """ remove script ext """
    def run(self):
        install_scripts.install_scripts.run(self)
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
        print('running update-desktop-database')
        call('update-desktop-database')


with open('README.rst') as f:
    long_description = f.read()

setup(name=__app_name__.lower(),
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
      ],
      package_dir={'rsteditor': 'rsteditor'},
      data_files=[
          ('share/%s' % __app_name__.lower(), [
              'README.rst',
              'MANIFEST.in',
              'rst.properties',
          ]),
          ('share/applications', ['rsteditor.desktop']),
          ('share/%s/template' % __app_name__.lower(), glob.glob('template/*.*')),
          ('share/%s/docs' % __app_name__.lower(), glob.glob('docs/*.rst')),
          ('share/%s/docs/images' % __app_name__.lower(), glob.glob('docs/images/*')),
      ],
      scripts=['rsteditor.py'],
      requires=['docutils', 'pygments', 'pyqt4', 'sip'],
      ext_modules=[
          Extension("rsteditor/scilexerrest",
                    [
                        "rsteditor/scilexerrest.sip",
                        "rsteditor/scilexerrest.cpp"
                    ],
                    include_dirs=[
                        '/usr/include/QtCore',
                        '/usr/include/QtGui',
                        'rsteditor',
                    ],
                    #library_dirs=[''],
                    libraries=['qscintilla2'],
                    ),
      ],
      cmdclass={
          'install_scripts': post_install_scripts,
          'install_data': post_install_data,
          'build_ext': my_build_ext,
      },
      # for py2exe
      windows=['rsteditor.py'],
      options={'py2exe': {
          'skip_archive': True,
          'dll_excludes': ['msvcp90.dll'],
          'includes': [
              'pygments',
              'ConfigParser',
              'docutils',
              'PyQt4.QtNetwork',
              'sip',
          ],
          'excludes': [],
      }}
      )
