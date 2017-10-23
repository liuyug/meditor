#!/usr/bin/env python3
# -*- encoding:utf-8 -*-

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


class install_desktop(install):
    def run(self):
        desktop_path = 'meditor.desktop'
        with open(desktop_path, 'wt') as f:
            f.write(desktop)
        install.run(self)


with open('README.rst') as f:
    long_description = f.read()

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
        ('share/pixmaps', ['meditor/share/pixmaps/meditor-text-editor.ico']),
        ('share/applications', ['meditor.desktop'])
    ],
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
