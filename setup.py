#!/usr/bin/env python3
# -*- encoding:utf-8 -*-

import os
import fnmatch
from setuptools import setup
from setuptools.command.install import install

from meditor import __app_name__
from meditor import __app_version__


desktop = """[Desktop Entry]
Version=%s
Name=Markup Editor
Comment=Editor for reStructedText and Markdown
Exec=meditor
MimeType=text/plain;
Icon=meditor-text-editor
Terminal=false
Type=Application
Categories=Application;Office;
StartupNotify=true
""" % __app_version__


with open('README.rst') as f:
    long_description = f.read()


class install_desktop(install):
    def run(self):
        desktop_path = 'meditor.desktop'
        with open(desktop_path, 'wt') as f:
            f.write(desktop)
        install.run(self)


def get_data_files(dest, src, patterns=None):
    if not patterns:
        patterns = ['*']
    data_files = []
    for root, dirnames, filenames in os.walk(src):
        if not filenames:
            continue
        files = []
        for pattern in patterns:
            for filename in fnmatch.filter(filenames, pattern):
                files.append(os.path.join(root, filename))
        if files:
            dest_path = os.path.join(dest, os.path.relpath(root, src))
            data_files.append([dest_path, files])
    return data_files


setup(
    name=__app_name__.lower(),
    version=__app_version__,
    author='Yugang LIU',
    author_email='liuyug@gmail.com',
    url='https://github.com/liuyug/meditor.git',
    license='GPLv3',
    description='Editor for ReStructedText and Markdown',
    long_description=long_description,
    platforms=['noarch'],
    packages=[
        'meditor',
        'meditor.scilib',
    ],
    include_package_data=True,
    data_files=[
        ('share/applications', ['meditor.desktop']),
    ] + get_data_files('share', 'meditor/share', '*'),
    entry_points={
        'console_scripts': [
            'meditor = meditor.app:main',
        ],
    },
    cmdclass={
        'install': install_desktop,
    },
    zip_safe=False,
)
