=========
RSTEditor
=========
|version| |download|

RSTEditor is a editor for ReStructedText. It support preview with html.

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
+ Syntax Highlight for ReStructedText
+ HTML Preview
+ Customized rst properties
+ Synchronize scroll with preview window
+ File system explorer
+ Customized widnow layout
+ ReStructedText Template to reduce extra work
+ Customized HTML css

HTML theme
===========
#. Download rhythm.css_

#. Unzip it to configuration directory.

   + It is "C:\\Users\\Administrator\\.config\\rsteditor\\themes\\" in Window 7.
   + It is "$HOME/.config/rsteditor/themes" in Linux.

#. Create theme file, "theme.json" under "rhythm.css" direcotry.

::

    {
        "stylesheet_path":"dist/css/rhythm.css,syntax/molokai.css",
        "syntax-highlight": "short"
    }

.. _rhythm.css: https://github.com/Rykka/rhythm.css/archive/master.zip

Install
=======
in Linux::

    pip install rsteditor-qt

or install it in user directory::

    pip install rsteditor-qt --user

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
