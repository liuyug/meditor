#!/bin/bash

(
echo "Get MathJax file..."

MATHJAX="MathJax-master.zip"
cur_dir=`pwd`

rm -f $MATHJAX
wget https://github.com/mathjax/MathJax/archive/master.zip -O $MATHJAX

mkdir -p meditor/share/meditor
cd meditor/share/meditor
rm -rf MathJax-master

unzip "$cur_dir/$MATHJAX"
)


# vim: tabstop=4 shiftwidth=4 expandtab
