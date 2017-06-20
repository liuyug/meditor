#!/usr/bin/env python3
# -*- encoding:utf-8 -*-

# tips:
#   pyqt 5.5.1 is compiled with msvc 2010
#   to build extention it need to install qt-5.5.1 with msvc2010

# import os.path

from setuptools import setup, Extension

# import sipdistutils
# import sipconfig
# import PyQt5
# from PyQt5.QtCore import PYQT_CONFIGURATION

from rsteditor import __app_name__
from rsteditor import __app_version__


# sip_cfg = sipconfig.Configuration()
# if sip_cfg.platform == 'win32':
#     qt_path = 'C:\\Qt\\Qt5.7.0\\5.7\\msvc2015'
# else:
#     qt_path = '/usr/include'
# pyqt_path = os.path.dirname(PyQt5.__file__)


# scilexerrest = Extension(
#     "rsteditor.scilexer.scilexerrest",
#     [
#         "rsteditor/scilexer/scilexerrest.sip",
#         "rsteditor/scilexer/scilexerrest.cpp"
#     ],
#     include_dirs=[
#         'rsteditor/scilexer',
#         os.path.join(qt_path, 'include'),
#         os.path.join(qt_path, 'include', 'QtCore'),
#         os.path.join(qt_path, 'include', 'QtGui'),
#         os.path.join(qt_path, 'include', 'QtWidgets'),
#     ],
#     define_macros=[
#         ('QSCINTILLA_DLL', None),   # only for window msvc
#     ],
#     library_dirs=[
#         os.path.join(qt_path, 'lib'),
#     ],
#     libraries=[
#         'qscintilla2',
#         'Qt5PrintSupport', 'Qt5Widgets', 'Qt5Gui', 'Qt5Core',
#     ],
#     # swig_opts=[
#     #     '-I', os.path.join(pyqt_path, 'sip', 'PyQt5'),
#     # ] + PYQT_CONFIGURATION.get('sip_flags', '').split(' '),
# )


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
        'rsteditor.scilib',
    ],
    include_package_data=True,
    # ext_modules=[scilexerrest],
    # cmdclass={
    #     'build_ext': sipdistutils.build_ext,
    # },
    entry_points={
        'console_scripts': [
            'rsteditor = rsteditor.app:main',
        ],
    },
    zip_safe=False,
)
