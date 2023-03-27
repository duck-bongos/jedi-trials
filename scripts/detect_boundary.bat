:: Detect the boundary for the input files

:: check the directories exist
@if not exist data\source (
	echo No source directory. Exiting...
	goto :end
	@if not exist data\target\ (
		echo No target directory. Exiting...
		goto :end
	)
)

@if not exist boundary_detection\mediapipe_mesh\requirements.txt (
	echo please put the requirements.txt file in the boundary_detection\mediapipe_mesh directory.
	exit 1
)
:: create a new python3 environment & install requirements
@echo Creating a virtual environment...
python3 -m venv tmp

@echo Created a virtual environment "tmp"
@echo Activating the virtual environment...

@call tmp\Scripts\activate
echo Activated the virtual environment tmp. Confirming activation...	

echo Installing the dependencies...
pip3 install -r boundary_detection\mediapipe_mesh\requirements.txt

where python3
python3 --version

echo Installation complete.
echo Entering boundary detection

:: navigate to the mediapipe_mesh directory
:: chdir .\boundary_detection\mediapipe_mesh\
pushd boundary_detection\mediapipe_mesh
echo Moving to new working directory: %CD%

echo Detecting boundary now...

:: For now, enforce the data directory is at the top level
python3 main.py

echo Completed boundary detection, tearing down...

:: return to top level
popd
echo Returned to top level: %CD%

:end