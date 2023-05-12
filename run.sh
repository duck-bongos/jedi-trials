#!/bin/bash
BUILD=0
CLEAN=0
SKIP_BD=0
ZIPDATA=0
PYENV=0
METRICS=0
STAGE="setup"

while getopts 'bcd:mpsz' flag
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
        m)
            METRICS=1
            ;;
        p)
            PYENV=1
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
    zip -r $1/data.zip ./data/mapped ./data/transformed
}

zip_stats() {
    zip -r $1/statistics.zip ./data/statistics/ runtime.txt
}

# prepend output
p() { 
    args=${@:2}; 
    $@ | sed "s/^/[$args]\\n/"
}

prep_stage() {
    $@ | sed "s/^/[$STAGE]\\n/" 
}

main () {
    if [[ $SKIP_BD == 1 ]]
    then
        STAGE="Boundary Detection"
        prep_stage echo "Boundary detection" >> runtime.txt
        prep_stage /usr/bin/time -a -h -o runtime.txt ./scripts/detect_boundary.sh -k

        # collapse the edges
        STAGE="QECD"
        prep_stage echo "Quadric Edge Collapse Decimation" >> runtime.txt
        prep_stage /usr/bin/time -a -h -o runtime.txt ./scripts/qecd.sh 1

    else
        STAGE="Boundary Detection"
        prep_stage echo "Boundary detection" >> runtime.txt
        prep_stage /usr/bin/time -a -h -o runtime.txt ./scripts/detect_boundary.sh

        # collapse the edges
        STAGE="QECD"
        echo "Quadric Edge Collapse Decimation" >> runtime.txt
        prep_stage /usr/bin/time -a -h -o runtime.txt ./scripts/qecd.sh

    fi

    # Compute the harmonic map
    STAGE="Harmonic Mapping"
    echo "Harmonic Map" >> runtime.txt
    prep_stage /usr/bin/time -a -h -o runtime.txt ./scripts/run_harmonic_map.sh

    # compute the mobius transform
    STAGE="Möbius Transform"
    echo "Möbius transform" >> runtime.txt
    prep_stage /usr/bin/time -a -h -o runtime.txt ./scripts/mobius.sh

    # compute the non rigid registration
    STAGE="Non-Rigid Registration"
    echo "Non-Rigid Registration" >> runtime.txt
    prep_stage /usr/bin/time -a -h -o runtime.txt ./scripts/nrr.sh

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
    STAGE="Cleaning"
    echo -e "Cleaning directories first..."
    echo "Cleaning" >> runtime.txt
    prep_stage /usr/bin/time -a -h -o runtime.txt ./clean.sh -b

    STAGE="Building"
    echo -e "Building requirements before the run..."
    echo "Building" >> runtime.txt
    prep_stage /usr/bin/time -a -h -o runtime.txt  ./scripts/build_all.sh

elif [[ $BUILD == 1 ]]
then
    STAGE="Building"
    echo -e "Building requirements before the run..."
    echo "Building" >> runtime.txt
    prep_stage /usr/bin/time -a -h -o runtime.txt  ./scripts/build_all.sh

elif [[ $CLEAN == 1 ]]
then
    STAGE="Cleaning"
    echo -e "Cleaning directories first..."
    echo "Cleaning" >> runtime.txt
    prep_stage /usr/bin/time -a -h -o runtime.txt  ./clean.sh
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
    STAGE="Zip Data"
    echo "Zipping data and sending to $DIRPATH ..."
    prep_stage zip_data "$DIRPATH"
    echo "Zipping complete!"
fi

if [[ $METRICS == 1 && ! -z "$DIRPATH" ]]
then
    STAGE="Zip Stats"
    echo "Zipping statistics and sending to $DIRPATH ..."
    prep_stage zip_stats "$DIRPATH"
    echo "Zipping complete!"
fi