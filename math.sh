#!/bin/bash

(
echo "Get MathJax single file..."

mkdir -p meditor/share/meditor/math
cd meditor/share/meditor/math

rm -f MathJax.min.js
wget https://github.com/pkra/MathJax-single-file/raw/master/dist/TeXCommonHTMLTeX/MathJax.min.js
)


# vim: tabstop=4 shiftwidth=4 expandtab
