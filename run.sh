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
shift "$(($OPTIND -1))"


data_copy() {
    # copy the source and target to the data directory
    find "$1" -maxdepth 1 -mindepth 1 -type f | while read -r fi; do
        echo "Copying $fi"
        f="$(basename -- $fi)"
        cp $fi data/$f
    done
}

main () {
    echo "Data Copy from $1" >> runtime.txt
    data_copy $1

    if [[ $SKIP_BD == 0 ]]
    then
        echo "Boundary detection" >> runtime.txt
        /usr/bin/time -a -h -o runtime.txt ./scripts/detect_boundary.sh 
    fi

    # collapse the edges
    echo "Quadric Edge Collapse Decimation" >> runtime.txt
    /usr/bin/time -a -h -o runtime.txt ./scripts/qecd.sh

    # Compute the harmonic map
    echo "Harmonic Map" >> runtime.txt
    /usr/bin/time -a -h -o runtime.txt ./scripts/run_harmonic_map.sh

    # compute the mobius transform
    echo "Möbius transform" >> runtime.txt
    /usr/bin/time -a -h -o runtime.txt ./scripts/mobius.sh

    # compute the non rigid registration
    echo "Non-Rigid Registration" >> runtime.txt
    /usr/bin/time -a -h -o runtime.txt ./scripts/nrr.sh

    # detect the boundary
    echo -e "\n----------------------------------------"
    echo -e "Run complete!"
    echo -e "----------------------------------------\n"
    cat runtime.txt
}

# # pass in the first argument as the dirpath
# if [[ ! -z $1 && -d "$1" && -z "$DIRPATH" ]]
# then
#     DIRPATH=$1
#     echo "DIRPATH set to $DIRPATH"
# fi

# set the scripts in the scripts directory to be executable
chmod -R 755 scripts
rm -rf runtime.txt
touch runtime.txt

# clean the directory pertaining to boundary detection
# runs boundary_clean.sh, map_clean.sh
if [[ $CLEAN == 1 && $BUILD == 1 ]]
then
    echo -e "Cleaning directories first..."
    echo "Cleaning" >> runtime.txt
    /usr/bin/time -a -h -o runtime.txt  ./clean.sh -b

    echo -e "Building requirements before the run..."
    echo "Building" >> runtime.txt
    /usr/bin/time -a -h -o runtime.txt  ./scripts/build_all.sh

elif [[ $BUILD == 1 ]]
then
    echo -e "Building requirements before the run..."
    echo "Building" >> runtime.txt
    /usr/bin/time -a -h -o runtime.txt  ./scripts/build_all.sh

elif [[ $CLEAN == 1 ]]
then
    echo -e "Cleaning directories first..."
    echo "Cleaning" >> runtime.txt
    /usr/bin/time -a -h -o runtime.txt  ./clean.sh
fi

echo "Skip $SKIP_BD"
echo "Build: $BUILD";
echo "Clean: $CLEAN";
echo "Recurse: $RECURSE";
echo "Dirpath: $DIRPATH";

if [[ $RECURSE == 0 ]]
then
    main "$DIRPATH"
else
    find "$DIRPATH" -maxdepth 1 -mindepth 1 -type d | while read -r dir; do
        if [[ ! "$dir" == "../data//.DS_STORE" ]]
        then
            echo "Running on $dir" >> runtime.txt
            main "$dir"
        fi
    done
fi


