# run EVERYTHING

# set the scripts in the scripts directory to be executable
chmod -R 755 scripts

# clean the directory pertaining to boundary detection
# runs boundary_clean.sh, map_clean.sh
./clean.sh

# detect the boundary
./scripts/detect_boundary.sh

# collapse the edges
./scripts/qecd.sh

# detect the mapping & mobius transform
./scripts/run_harmonic_map.sh

# compute the mobius transform
# ./scripts/mobius.sh

# compute the non rigid registration
# ./scripts/nrr.sh

# visualization


echo -e "\n----------------------------------------"
echo -e "Run complete!"
echo -e "----------------------------------------\n"