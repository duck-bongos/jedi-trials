# jedi-trials
This repository will host all the code that will be part of my Master's thesis at Stony Brook University

### Requirements:
***
This project was built on both MacOS and Windows 10. It has _not_ been tested on Linux. 
Please see `./system/specifications/<os>_specs.md` for more information.

### Installation:
***
Optional! If you want to pre-build into a Python environment, you can run 
> `pip3 install -r requirements.txt`

Otherwise, all Python packages are built during the run.

All code in C++ is either written using `stdlib` or is included in `3rdParty` subdirectories.


### Pipeline
***
1. Boundary Detection
2. Quadric Edge Collapse Decimation
3. Harmonic Mapping 
4. Möbius Transformation 
5. Non-Rigid Registration

### Usage
***
Depending on your OS, you will either use
> `./run.sh`

or 
> `run.bat`

to run the entire pipeline. You can add in arguments "clean" or "build" if you want to have a clean run or aren't sure whether all the executables are built. Here's an example:
> `./run.sh clean build`

This will clean out the relevant data directories, rebuild the executables, and run the pipeline. Order does _not_ matter - cleaning occurs before rebuilding if both are present.


`run` calls all the other computational scripts (located in `./scripts/`) in the order listed in the pipeline. For convenience's sake, if you only wish to use or run part of the pipeline, it has been broken down modularly so you can both run and clean each part

### Table of Contents:
***
 - boundary_detection: Location for all boundary detection code.
 - data: Where all data is located for before, during, and after runs. See `data/README.md` for more details.
 - docs: Documentation directory
 - optimization: Location for all optimization method code.
 - scripts: Where all command line scripts for MacOS and Windows are stored.
 - system: Information that may help users us the system.
 - `<tmp>`: A Python virtualenv that is used during the run
 - `clean.(bat/sh)`: A script to clean out the files and directories before a run.
 - `requirements.txt`: A list of all necessary Python packages and their versions to run the pipeline.
 - `run.(bat/sh)`: A script to run boundary detection, optimization, and registration.
