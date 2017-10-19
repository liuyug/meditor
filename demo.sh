#!/bin/sh

set -e
set -x

share_docs=`pwd`/meditor/share/meditor/docs

mkdir -p docs/rst
mkdir -p $share_docs

(
cd docs/rst
wget http://docutils.sourceforge.net/docs/ref/rst/definitions.txt
wget http://docutils.sourceforge.net/docs/ref/rst/directives.txt
wget http://docutils.sourceforge.net/docs/ref/rst/introduction.txt
wget http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.txt
wget http://docutils.sourceforge.net/docs/ref/rst/roles.txt
)

(
cd docs
wget http://docutils.sourceforge.net/docs/user/rst/
)

# vim: tabstop=4 shiftwidth=4 expandtab
