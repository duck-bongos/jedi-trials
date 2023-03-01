# jedi-trials
This repository will host all the code that will be part of my Master's thesis at Stony Brook University

### As of 2/20, Must be run on a windows machine - ICP using PCL doesn't work on MacOS

## Prerequisites, dependencies, and set up
* Need Point Cloud Library
* [PCL Tutorials](https://pcl.readthedocs.io/projects/tutorials/en/master/)
* [Compiling PCL step-by-step](https://pcl.readthedocs.io/projects/tutorials/en/master/compiling_pcl_macosx.html#compiling-pcl-macosx)
* [Installing PCL with homebrew](https://pcl.readthedocs.io/projects/tutorials/en/master/installing_homebrew.html#installing-homebrew)
* [MediaPipe in C++ Installation](https://google.github.io/mediapipe/getting_started/cpp.html)
* [MediaPipe Hello World](https://google.github.io/mediapipe/getting_started/hello_world_cpp.html)


# Roadmap
### Hypothesis
The NRR solution accuracy will be higher using a consistent boundary than with an inconsistent boundary.

### Inputs
4 files: 
----
2 source: 2D image (.png), 3D object meshes (.obj)
2 target: 2D image (.png), 3D object meshes (.obj)


### Method
1. Take source 2D image
2. run MediaPipe on it to get a canonical face 
3. Use ICP on our mesh & mediapipe mesh <-- Consistent Boundary
4. Repeat 1-3 for target image
5. Take all points inside boundary  <-- Boundary snipping
6. ICP on source & target face  <-- Solve NRR

### UPDATE: C++ Compatibility
After 7.5 hours of effort, I learned it is not possible to include MediaPipe in a C++ project. 
Therefore, I decided to do the work in Python using [Numpy](https://numpy.org/), [OpenCV](https://opencv.org/), [Shapely](https://shapely.readthedocs.io/en/stable/index.html), and [MediaPipe](https://google.github.io/mediapipe/). All versions included at `boundary_detection/mediapipe_mesh/requirements.txt`.
