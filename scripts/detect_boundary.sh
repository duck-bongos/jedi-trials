# Detect the boundary for the input files

# check the object files exist
[[ -f data/source.obj ]] && [[ -f data/target.obj ]]

# check the image files exist
[[ -f data/source.png ]] && [[ -f data/target.png ]]

# navigate to the boundary_detection directory
cd boundary_detection/

# for now, enforce the data directory is at the top level

# run all the full boundary examples
echo "Running consistent boundary examples..."
for b in boundaries/*.txt; do
    echo $b
    python3 main.py -i ../data/source.png -o ../data/source.obj -b $b
    python3 main.py -i ../data/target.png -o ../data/target.obj -b $b
done
echo "Completed consistent boundary examples."
echo; echo
echo "Running inconsistent boundary examples..."
for b in boundaries/*.txt; do
    bb="$(basename -- "$b")"
    bx="${bb%.*}"
    for s in inconsistent_boundaries/*; do
        basename="$(basename "$s")"
        if [[ "$basename" == "$bx" ]]; then
            for c in $s/*.txt; do
                python3 main.py -i ../data/source.png -o ../data/source.obj -b $b -c $c
            done
        fi
    done
done
echo "Completed inconsistent boundary examples."

echo -e "Completed boundary detection."

# return to the top level directory
cd ..


if [[ -d tmp ]]
then
	echo -e "tmp directory exists, tearing down..."
	# turn off the virtual environment
	deactivate

	# remove the virtual environment
	rm -rf tmp
	echo -e "Teardown complete."
fi

echo -e "Boundary detection complete."