=============
Markup Editor
=============
|version| |download|

Markup Editor is a editor for reStructuredText and Markdown.

.. tip::

   For bad performance, close "preview on input".

Feature
=======
+ support Markdown and reStructedText
+ Syntax Highlight for reStructuredText
+ support MathJax
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

    # download source
    git clone https://github.com/liuyug/meditor.git
    cd meditor

    # for Virtualenv
    virtualenv ../virtualenv
    # on Linux
    source ../virtualenv/bin/activate
    # on Window cmd
    ../virtualenv/scripts/activate
    # on Window PowerShell
    Set-ExecutionPolicy -Scope CurrentUser  RemoteSigned
    ../virtualenv/scripts/activate

    # check version
    python --version
    pip --version

    # install 3rd packages
    pip install -r requirements.txt
    # prepre data files
    bash ui.sh
    bash math.sh
    bash themes.sh
    # install meditor
    pip install .

    # update latest meditor
    pip3 install meditor

or install it in user directory::

    pip3 install meditor --user

.. note::

    `Travis <travis-ci.org>`_ don't run with GUI application. It always build failure.

HTML theme
===========
get theme::

    bash themes.sh

Screen Shot
===========
.. image:: screenshot.png

.. |version| image:: https://img.shields.io/pypi/v/meditor.svg
   :target: https://pypi.python.org/pypi/meditor
   :alt: Version

.. |download| image:: https://img.shields.io/github/downloads/liuyug/meditor/total.svg
   :target: https://pypi.python.org/pypi/meditor
   :alt: Downloads

Other
======
Iconset: `NuoveXT 2`_ Icons by Saki

.. _`NuoveXT 2`: http://www.iconarchive.com/show/nuoveXT-2-icons-by-saki.2.html
