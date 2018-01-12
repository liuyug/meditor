#!/usr/bin/env python3
# -*- encoding:utf-8 -*-

import os
import fnmatch
from setuptools import setup, find_packages
from setuptools.command.install import install

from meditor import __app_version__


desktop = """[Desktop Entry]
Version=%s
Name=Markup Editor
Comment=Editor for reStructuredText and Markdown
Exec=meditor
MimeType=text/plain;
Icon=accessories-text-editor
Terminal=false
Type=Application
Categories=Application;Office;
StartupNotify=true
""" % __app_version__


with open('README.rst') as f:
    long_description = f.read()

requirements = []
with open('requirements.txt') as f:
    for line in f.readlines():
        line.strip()
        if line.startswith('#'):
            continue
        requirements.append(line)


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
    name='meditor',
    version=__app_version__,
    author='Yugang LIU',
    author_email='liuyug@gmail.com',
    url='https://github.com/liuyug/meditor.git',
    license='GPLv3',
    description='Editor for reStructuredText and Markdown',
    long_description=long_description,
    keywords='reStructuredText Markdown editor preview',
    python_requires='>=3',
    platforms=['noarch'],
    packages=find_packages(),
    data_files=[
        ('share/applications', ['meditor.desktop']),
    ] + get_data_files('share', 'meditor/share', '*'),
    entry_points={
        'gui_scripts': [
            'meditor = meditor.app:main',
        ],
    },
    cmdclass={
        'install': install_desktop,
    },
    install_requires=requirements,
    zip_safe=False,
)
