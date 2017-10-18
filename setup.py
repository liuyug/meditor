#!/usr/bin/env python3
# -*- encoding:utf-8 -*-

from setuptools import setup

from rsteditor import __app_name__
from rsteditor import __app_version__


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
    entry_points={
        'console_scripts': [
            'rsteditor = rsteditor.app:main',
        ],
    },
    zip_safe=False,
)
