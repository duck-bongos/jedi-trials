# clean both the boundary detection and mapping
./scripts/boundary_clean.sh
.scripts/keypoints_clean.sh
./scripts/collapsed_clean.sh
./scripts/map_clean.sh

if [ -d tmp ] && [ -f tmp/bin/activate] 
then
    rm -rf tmp
fi