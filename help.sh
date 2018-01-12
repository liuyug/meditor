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

share_help=`pwd`/meditor/data/help

rm -rf help

# reStructuredText
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

# Markdown
(
cd help
wget https://daringfireball.net/projects/markdown/basics.text
wget https://daringfireball.net/projects/markdown/syntax.text

rename .text .md
)

# copy help to application
mkdir -p $share_help
(
cd help
cp -rf * $share_help
)



# vim: tabstop=4 shiftwidth=4 expandtab
