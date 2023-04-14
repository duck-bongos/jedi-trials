# Scripts
Here you can find all the modular scripts for working with pieces of the pipeline. Names were determined for the user's convenience's sake - no name begins with the same two letters (within a file extension type).

## Table of Contents
Every script has a duplicate bash script (`.sh`) and windows batch file (`.bat`). Every pipeline module has an associated cleaning script.
***
 - boundary_clean:
 - build_all: Build all the executables and the Python environment.
 - clean_build: Remove all executables and the Python environment.
 - collapsed_clean: Remove objects from `data/transformed`.
 - detect_boundary: Run boundary detection on the face images and objects.
 - keypoints_clean: Remove objects from `data/keypoints`.
 - map_clean: Remove objects from `data/mapped`.
 - mobius: Run a Möbius transformation on predetermined data.
 - nrr: Run non-rigid registration with a KNN.
 - qecd: Run Quadric Edge Collapse Decimation.
 - registration_clean: Remove objects from `data/registration`.
 - run_harmonic_map: Run the harmonic map optimization.
 - transformed_clean: Remove objects from `data/transformed` directory.