# jedi-trials
This repository will host all the code that will be part of my Master's thesis at Stony Brook University

### As of 2/20, Must be run on a windows machine - ICP using PCL doesn't work on MacOS
### As of approx 2/23, ICP using PCL is a display purpose only library

## Prerequisites, dependencies, and set up
* Need Point Cloud Library
* [PCL Tutorials](https://pcl.readthedocs.io/projects/tutorials/en/master/)
* [Compiling PCL step-by-step](https://pcl.readthedocs.io/projects/tutorials/en/master/compiling_pcl_macosx.html#compiling-pcl-macosx)
* [Installing PCL with homebrew](https://pcl.readthedocs.io/projects/tutorials/en/master/installing_homebrew.html#installing-homebrew)
* [MediaPipe in C++ Installation](https://google.github.io/mediapipe/getting_started/cpp.html)
* [MediaPipe Hello World](https://google.github.io/mediapipe/getting_started/hello_world_cpp.html)


#### UPDATE: MediaPipe C++ Compatibility & Dependency Update
After 7.5 hours of effort, I learned it is not possible to include MediaPipe in a C++ project. It seems the only way to use mediapipe in a project is to download the library and put _your_ project into the mediapipe folder. Since I am much more well-versed in Python, I'm going to use MediaPipe's Python installation using

`pip install mediapipe`

and run it from there. I will do the rest of the work in Python using [Numpy](https://numpy.org/), [OpenCV](https://opencv.org/), [Shapely](https://shapely.readthedocs.io/en/stable/index.html), and [MediaPipe](https://google.github.io/mediapipe/). All versions of dependencies included at `./boundary_detection/mediapipe_mesh/requirements.txt`.

# Roadmap
### Hypothesis
The NRR solution accuracy will be higher using a consistent boundary than with an inconsistent boundary. We're using harmonic map to solve the NRR part.

### Method (Updated 3/21/23)
1. Take source 2D image
2. run MediaPipe on it to get a canonical face
3. Use Numpy and OpenCV to extract "consistent" boundary
4. Create output `.obj` file with points inside the boundary.
5. Repeat 2-4 for target image
6. Harmonic Map on source & target face  <-- Solve NRR
7. Evaluate metrics


### Inputs
4 files: 
----
2 source: 2D image (.png), 3D object meshes (.obj)
2 target: 2D image (.png), 3D object meshes (.obj)

### Usage
0. Ensure the inputs exist
1. navigate to the `./boundary_detection/mediapipe_mesh` directory
2. Run `pip install -r requirements.txt`
3. Run `python main.py`. If your input files aren't in the [specified](boundary_detection\mediapipe_mesh\src\utils.py:parse_cli) locations, you will need to use the CLI flags.
4. View the results in `./data/annotated/`. <-- See about how the program writes this out.

### Naming conventions
* `pixel`:
* `texture`:
* `voxel`:

