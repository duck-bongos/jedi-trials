#!/bin/bash
BUILD=0
while getopts 'bcd:Rs' flag
do
    case "$flag" in
        b) 
            BUILD=1
            ;;
        ?)
            echo -e "Illegal option. Usage: $(basename ) [-b]"
            exit 1
            ;;
    esac
done
# clean both the boundary detection and mapping
if [[ $BUILD == 1 ]] 
then
    ./scripts/clean_build.sh
    ./scripts/map_clean.sh
fi
./scripts/data_clean.sh
./scripts/boundary_clean.sh
./scripts/keypoints_clean.sh
./scripts/collapsed_clean.sh

./scripts/transformed_clean.sh
./scripts/registration_clean.sh

rm data/statistics/*.txt

if [ -d tmp ] && [ -f tmp/bin/activate] 
then
    rm -rf tmp
fi
