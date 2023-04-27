#!/bin/bash
BUILD=0
CLEAN=0
SKIP_BD=0
ZIPDATA=0

while getopts 'bcd:sz' flag
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
        s)
            SKIP_BD=1
            ;;
        z)
            ZIPDATA=1
            ;;
        ?) 
            echo -e "Illegal option. Usage: $(basename ) [-b] [-c] [-d <dirpath>] [-s] [-o <outpath>]" >&2
            exit 1
            ;;
    esac
done
shift "$(($OPTIND -1))"


data_copy() {
    # copy the source and target to the data directory
    find "$1" -maxdepth 1 -mindepth 1 -type f | while read -r fi; do
        f="$(basename -- $fi)"
        extension="${fi##*.}"
        if [[ $extension == "obj" || $extension == "png" ]]
        then
            echo "Copying $fi"
            cp $fi data/$f
        fi
    done
}

zip_data() {
    zip -r $1/data.zip ./data/
}

main () {
    if [[ $SKIP_BD == 1 ]]
    then
        echo "Boundary detection" >> runtime.txt
        /usr/bin/time -a -h -o runtime.txt ./scripts/detect_boundary.sh -k

        # collapse the edges
        echo "Quadric Edge Collapse Decimation" >> runtime.txt
        /usr/bin/time -a -h -o runtime.txt ./scripts/qecd.sh 1

    else
        echo "Boundary detection" >> runtime.txt
        /usr/bin/time -a -h -o runtime.txt ./scripts/detect_boundary.sh

        # collapse the edges
        echo "Quadric Edge Collapse Decimation" >> runtime.txt
        /usr/bin/time -a -h -o runtime.txt ./scripts/qecd.sh

    fi

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
echo "Dirpath: $DIRPATH";
echo "Zip Data: $ZIPDATA";

if [[ ! -z "$DIRPATH" ]]
then
    data_copy "$DIRPATH"
fi

main
echo 
if [[ $ZIPDATA == 1 && ! -z "$DIRPATH" ]]
then
    echo "Zipping data and sending to $DIRPATH ..."
    zip_data "$DIRPATH"
    echo "Zipping complete!"
fi