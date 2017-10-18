#!/bin/bash

set -e

uic='pyuic5'

ui_dir='meditor/ui'


for ui_file in `ls $ui_dir/*.ui`; do
    b=`basename $ui_file .ui`
    $uic -o "$ui_dir/ui_$b.py" $ui_file
done
