#!/bin/bash

if [ x"$1" == "x" ]; then
    themes=`python3 icon_theme.py --list`
    echo "Usage: $0 <theme name>"
    echo "current themes:"
    echo "    $themes"
    exit 1
fi

theme=$1

theme_py=qrc_icon_theme.py
theme_qrc=theme.qrc


python3 icon_theme.py --collect meditor --theme $theme --qrc $theme_qrc
pyrcc5 -o meditor/$theme_py $theme_qrc

# rm -f $theme_qrc

