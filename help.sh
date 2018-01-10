#!/bin/sh

set -e
set -x

rename()
{
    for f in `ls *$1`; do
        b=`basename $f $1`
        mv $f $b$2
    done
}

share_help=`pwd`/meditor/share/meditor/help

rm -rf help

(
mkdir -p help
cd help
wget http://docutils.sourceforge.net/sandbox/jensj/latex_math/docs/latex_math.txt

rename .txt .rst
)

(
mkdir -p help/ref
cd help/ref
wget http://docutils.sourceforge.net/docs/ref/rst/definitions.txt
wget http://docutils.sourceforge.net/docs/ref/rst/directives.txt
wget http://docutils.sourceforge.net/docs/ref/rst/introduction.txt
wget http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.txt
wget http://docutils.sourceforge.net/docs/ref/rst/roles.txt

rename .txt .rst
)

(
mkdir -p help
cd help
wget http://docutils.sourceforge.net/docs/user/rst/cheatsheet.txt
wget http://docutils.sourceforge.net/docs/user/rst/demo.txt
wget http://docutils.sourceforge.net/docs/user/rst/quickstart.txt

rename .txt .rst
mkdir -p images
(
cd images
wget http://docutils.sourceforge.net/docs/user/rst/images/biohazard.png
wget http://docutils.sourceforge.net/docs/user/rst/images/title.png
)
)

mkdir -p $share_help
(
cd help
cp -rf * $share_help
)

# vim: tabstop=4 shiftwidth=4 expandtab
