=========
RSTEditor
=========
|version| |download|

RSTEditor is a editor for reStructuredText It support preview with html.

.. tip::

   For better performance, close "preview on input".

Feature
=======
+ Syntax Highlight for reStructuredText
+ HTML Preview
+ Customized rst properties
+ Synchronize scroll with preview window
+ File system explorer
+ Customized widnow layout
+ reStructuredText Template to reduce extra work
+ Customized HTML css

Install
=======
in Linux::

    pip install rsteditor-qt

or install it in user directory::

    pip install rsteditor-qt --user

in Window:

Please download win32_ installer file.

.. _win32: https://sourceforge.net/projects/rsteditor/files/latest/download?source=files

HTML theme
===========
get theme::

    sh themes.sh

Screen Shot
===========
.. image:: screenshot.png

.. |version| image:: https://img.shields.io/pypi/v/rsteditor.png
   :target: https://pypi.python.org/pypi/rsteditor
   :alt: Version

.. |download| image:: https://img.shields.io/pypi/dm/rsteditor.png
   :target: https://pypi.python.org/pypi/rsteditor
   :alt: Downloads

Requirement
===========
Install them on all platform:

+ docutils
+ Pygments
+ pyqt4/pyqt5
+ sip

some packages for debian/ubuntu
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    apt-get install python3-pyqt5 python3-pyqt5.qtwebkit python3-pyqt5.qsci
    apt-get install python3-sip python3-sip-dev pyqt5-dev pyqt5.qsci-dev
    apt-get install qt5-default libqt5scintilla2-dev
    apt-get install python3-pkgconfig

for develop
~~~~~~~~~~~~
install with below order:

#. download qt and install
#. download QScintilla source, compile and install
#. download sip source, compile and install
#. download pyqt source, compile and install

   pyqt with binary version compiled by msvc

#. compile QScintilla for pyqt and install

.. tip::

    check current compiler::

        python setup.py build_ext --help-compiler

.. note::

    Windows Python is built in Microsoft Visual C++; using other compilers may
    or may not work (though Borland seems to).

.. note::

    from qsciglobal.h
    // Under Windows, define QSCINTILLA_MAKE_DLL to create a Scintilla DLL, or
    // define QSCINTILLA_DLL to link against a Scintilla DLL, or define neither
    // to either build or link against a static Scintilla library.


Other
======
Iconset: `NuoveXT 2`_ Icons by Saki

.. _`NuoveXT 2`: http://www.iconarchive.com/show/nuoveXT-2-icons-by-saki.2.html
