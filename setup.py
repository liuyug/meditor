#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import os
import sys
import glob

from distutils.core import setup
import distutils.command.install_scripts
try:
    import py2exe
except:
    pass

from rsteditor import __app_name__
from rsteditor import __app_version__

class my_install(distutils.command.install_scripts.install_scripts):
    """ remove script ext """
    def run(self):
        distutils.command.install_scripts.install_scripts.run(self)
        if sys.platform == 'win32':
            for script in self.get_outputs():
                if script.endswith(".py"):
                    os.rename(script, '%s_gui.py'% script[:-3])
        else:
            for script in self.get_outputs():
                if script.endswith(".py"):
                    os.rename(script, script[:-3])
        return

with open('README.rst') as f:
    long_description=f.read()

setup(name=__app_name__.lower(),
      version=__app_version__,
      author='Yugang LIU',
      author_email='liuyug@gmail.com',
      url='https://github.com/liuyug/',
      license='GPLv3',
      description='Editor for ReStructedText',
      long_description=long_description,
      platforms=['noarch'],
      packages=[
          'rsteditor',
      ],
      package_dir = {'rsteditor': 'rsteditor'},
      data_files = [
          ('share/%s'% __app_name__.lower(), [
              'README.rst',
              'MANIFEST.in',
              ]),
          ('share/%s/template'% __app_name__.lower(), glob.glob('template/*.*')),
          ('share/%s/docs'% __app_name__.lower(), glob.glob('docs/*.rst')),
          ('share/%s/docs/images'% __app_name__.lower(), glob.glob('docs/images/*')),
          ],
      scripts=['rsteditor.py'],
      requires=['docutils', 'pygments', 'pyqt4'],
      cmdclass = {"install_scripts": my_install},
      # for py2exe
      windows=['rsteditor.py'],
      options={'py2exe':{
          'skip_archive':True,
          'dll_excludes':['msvcp90.dll'],
          'includes':[
              'pygments',
              'ConfigParser',
              'docutils',
              ],
          'excludes':[
              ],
          },}
      )


