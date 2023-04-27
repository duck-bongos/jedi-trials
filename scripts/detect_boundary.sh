# Detect the boundary for the input files

# check the object files exist
[[ -f data/source.obj ]] && [[ -f data/target.obj ]]

# check the image files exist
[[ -f data/source.png ]] && [[ -f data/target.png ]]

# navigate to the boundary_detection directory
cd boundary_detection/

# if [[ ! -z $1 ]]
# then
# 	echo $1
# fi

# for now, enforce the data directory is at the top level
python main.py $1

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

