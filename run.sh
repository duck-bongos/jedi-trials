# run EVERYTHING

# set the scripts in the scripts directory to be executable
chmod -R 755 scripts

# clean the directory pertaining to boundary detection
# runs boundary_clean.sh, map_clean.sh
./scripts/clean.sh

# detect the boundary
./scripts/detect_boundary.sh

# detect the mapping
./scripts/run_harmonic_map.sh

