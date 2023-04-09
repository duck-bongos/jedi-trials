# clean both the boundary detection and mapping
if [ $1 == "build" ] 
then
    ./scripts/clean_build.sh
fi

./scripts/boundary_clean.sh
./scripts/keypoints_clean.sh
./scripts/collapsed_clean.sh
./scripts/map_clean.sh
./scripts/transformed_clean.sh
./scripts/registration_clean.sh

if [ -d tmp ] && [ -f tmp/bin/activate] 
then
    rm -rf tmp
fi