#!/bin/bash
if [[ -f $1 ]]
then
    echo "$1 is file."
    sed -i '' 's|^v \([0-9.\-]*\) \([0-9.\-]*\) \([0-9.\-]*\)|v \1 \2 0.0 |' $1
fi