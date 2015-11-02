=========
RSTEditor
=========
|version| |download|

RSTEditor is a editor for reStructuredText It support preview with html.

.. tip::

   For better performance, close "preview on input".

Requirement
===========
Install them on all platform:

+ docutils
+ Pygments
+ pyqt4
+ argparse
+ sip

For ubuntu::

    apt-get install python-qt4-dev
    apt-get install python-sip-dev
    apt-get install python-qscintilla2
    apt-get install python-docutils

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

HTML theme
===========
#. Download theme, such as rhythm.css_, `timhughes theme`_

#. Unzip it to configuration directory.

   + It is "C:\\Users\\Administrator\\.config\\rsteditor\\themes\\" in Window 7.
   + It is "$HOME/.config/rsteditor/themes" in Linux.

#. Create theme file, "theme.json" under theme direcotry.

Support parameter:

+ stylesheet_path
+ syntax_highlight
+ template

theme.json under rhythm.css::

    {
        "stylesheet_path":"dist/css/rhythm.css,syntax/molokai.css",
        "syntax-highlight": "short"
    }

theme.json under timhughes theme::

    {
        "stylesheet_path":"reset.css,goldfish.css,goldfish-pygments-long.css,goldfish-pygments-long-python.css",
        "syntax-highlight": "long"
    }

.. _rhythm.css: https://github.com/Rykka/rhythm.css/archive/master.zip
.. _`timhughes theme`: https://bitbucket.org/timhughes/restructuredtext-theme/get/0de88230f44a.zip

Install
=======
in Linux::

    pip install rsteditor-qt

or install it in user directory::

    pip install rsteditor-qt --user

in Window:

Please download win32_ installer file.

.. _win32: https://sourceforge.net/projects/rsteditor/files/latest/download?source=files

.. tip::

    check current compiler::

        python setup.py build_ext --help-compiler

.. note::

    Windows Python is built in Microsoft Visual C++; using other compilers may or may not work (though Borland seems to).

Template
========
template::

    skeleton.rst

Screen Shot
===========
.. image:: screenshot.png

.. |version| image:: https://img.shields.io/pypi/v/rsteditor.png
   :target: https://pypi.python.org/pypi/rsteditor
   :alt: Version

.. |download| image:: https://img.shields.io/pypi/dm/rsteditor.png
   :target: https://pypi.python.org/pypi/rsteditor
   :alt: Downloads

Other
======
Iconset: `NuoveXT 2`_ Icons by Saki


.. _`NuoveXT 2`: http://www.iconarchive.com/show/nuoveXT-2-icons-by-saki.2.html
