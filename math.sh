#!/bin/bash

(
echo "Get MathJax single file..."
cd meditor
rm -f MathJax.min.js
wget https://github.com/pkra/MathJax-single-file/raw/master/dist/TeXCommonHTMLTeX/MathJax.min.js
)


# vim: tabstop=4 shiftwidth=4 expandtab
