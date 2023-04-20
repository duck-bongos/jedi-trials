#!/bin/bash
BUILD=0
CLEAN=0
RECURSE=0
SKIP_BD=0

while getopts 'bcd:Rs' flag
do
    case "$flag" in
        b) 
            BUILD=1
            ;;
        c) 
            CLEAN=1
            ;;
        d) 
            DIRPATH=$OPTARG
            ;;
        R) 
            RECURSE=1
            ;;
        s)
            SKIP_BD=1
            ;;
        ?) 
            echo -e "Illegal option. Usage: $(basename ) [-b] [-c] [-d <dirpath>]" >&2
            exit 1
            ;;
    esac
done

# if [[ ! -z DIRPATH ]]
# then
#     echo "Please provide a directory path to run on."
#     exit 1
# fi
# if [[ ! -d DIRPATH ]]
# then
#     echo -e "$DIRPATH is not a directory."
#     exit 1
if [[ -d "$DIRPATH" ]]
then
    echo "$DIRPATH is a directory."
    echo "Recurse is $RECURSE"
fi
if [[ -d "$DIRPATH" && $RECURSE == 1 ]]
then
    find "$DIRPATH" -maxdepth 1 -mindepth 1 -type d | while read -r dir; do
        echo "Processing $dir"
        # Do whatever you want to do with each directory here
        find "$dir" -maxdepth 1 -mindepth 1 -type f | while read -r fi; do
            echo "Moving $fi"
            f="$(basename -- $fi)"
            cp $fi ../data/$f
        done
        
    done
fi

shift "$(($OPTIND -1))"
echo "Build: $BUILD";
echo "Clean: $CLEAN";
echo "Recurse: $RECURSE";
echo "Dirpath: $DIRPATH";