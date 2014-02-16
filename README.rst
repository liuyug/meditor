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

Feature
=======
+ Syntax Highlight for ReStructedText
+ HTML Preview
+ Customized rst properties
+ Synchronize scroll with preview window
+ File system explorer
+ Customized widnow layout
+ ReStructedText Template to reduce extra work

Py2exe
=======
To make a Py2exe package, you need copy docutils and pygments files into ``dist`` directory manually.

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
