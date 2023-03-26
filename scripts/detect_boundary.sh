# Detect the boundary for the input files

# check the directories exists
[ -d data/source ] && [ -d data/target ]

# check that the dependencies file exists
if [[ -f boundary_detection/mediapipe_mesh/requirements.txt ]]
then
	# create a new python3 environment & install requirements
	echo -e "Creating a virtual environment..."
	python3 -m venv tmp

	echo -e "Created virtual environment 'tmp'."
	
	echo -e "Activating the virtual environment..."
	source tmp/bin/activate

	which python3
	python3 --version


	echo -e "Installing the dependencies..."
	pip3 install -r boundary_detection/mediapipe_mesh/requirements.txt

fi

# navigate the the mediapipe_mesh directory
cd boundary_detection/mediapipe_mesh

# for now, enforce the data directory is at the top level
python main.py

echo -e "Completed boundary detection, tearing down..."

# return to the top level directory
cd ../..


if [ -d tmp ]
then
	# turn off the virtual environment
	deactivate

	# remove the virtualenvironment
	rm -rf tmp
fi

echo -e "Teardown complete."
