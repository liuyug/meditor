#!/bin/bash

(
echo "Get Single MathJax file..."

MATHJAX="MathJax.min.js"

mkdir -p meditor/data/math
cd meditor/data/math
rm -f $MATHJAX

wget https://github.com/pkra/MathJax-single-file/raw/master/dist/TeXCommonHTMLTeX/MathJax.min.js -O $MATHJAX
)


# vim: tabstop=4 shiftwidth=4 expandtab
