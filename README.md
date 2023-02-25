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

# Mediapipe in C++ Setup on MacOS
This took me about 3 hours due to version constraints, JDK availability, etc. I hope this helps you cut down on the time to install. 
### Resources:
I pulled helpful hints from multiple resources. They are cited using superscript notation below.
1. [Install MediaPipe tutorial](https://google.github.io/mediapipe/getting_started/install.html)
2. [Hello World! in C++ for MediaPipe](https://google.github.io/mediapipe/getting_started/hello_world_cpp.html)
3. [This super helpful GitHub issue link](https://github.com/google/mediapipe/issues/3660)
4. [Bazelisk GitHub](https://github.com/bazelbuild/bazelisk)
5. My own trial and error


### Assumptions: 
* You have root (`sudo`) access.^[5]^
* You have [homebrew installed](https://brew.sh/).^[1]^
* You have [Xcode installed](https://developer.apple.com/xcode/).^[1]^
* You are using a [Python version >= 3.10](https://www.python.org/downloads/). I used Python 3.11.1.^[5]^
* You have GitHub access and Git installed^[5]

### Instructions
1. Navigate to /usr/local/share/^[5]^
2. Clone the repository `git clone --depth 1 https://github.com/google/mediapipe.git` ^[1]^
3. `cd mediapipe`^[1]^
4. Install OpenCV3 `brew install opencv@3`^[1]^
5. Uninstall known issue with `glog`: `brew uninstall --ignore-dependencies glog`^[1]^
6. link Python 3.10+ to the python3 path `sudo ln -s -f /usr/local/bin/<python3.10+> /usr/local/bin/python`^[1]^
7. Ensure Python's "six" library is installed `pip3 install --user six`^[1]^
8. Install Bazelisk `brew install bazelisk` ^[4]^
8. Set up Bazel by running the following two commands[5]:
```
export USE_BAZEL_VERSION=5.2.0

bazelisk build
```
9. To run Mediapipe's hello_world example, we need to run the following commands:
```
export GLOG_logtostderr=1
# Need bazel flag 'MEDIAPIPE_DISABLE_GPU=1' as desktop GPU is currently not supported
$ bazel run --define MEDIAPIPE_DISABLE_GPU=1 \
    mediapipe/examples/desktop/hello_world:hello_world
```