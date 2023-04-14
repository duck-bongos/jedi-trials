if [ ! -f HarmonicMap/bin/map ]
then
    echo -e "executable doesn't exist. Building...\n"
    cd HarmonicMap

    # enter the build directory
    cd build
    cmake ..
    cmake --build .

    # return to optimization/HarmonicMap
    echo -e "Built HarmonicMap/bin/map\n"
    cd ../..

    echo $PWD

fi

if [ ! -f non_rigid_registration/nrr ]
then
    clang++ -std=c++11 non_rigid_registration/nrr.cc -o non_rigid_registration/nrr
    echo -e "Built non_rigid_registration/nrr"
fi

if [ ! -f mobius/mobius ]
then
    clang++ -std=c++11 mobius/mobius.cc -o mobius/mobius
    echo -e "Built mobius/mobius"
fi


if [ -f requirements.txt ]
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
	pip3 install -r requirements.txt

fi
