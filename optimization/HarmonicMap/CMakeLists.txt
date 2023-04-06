cmake_minimum_required(VERSION 3.6)

# Name the project
# project(CCGHomework)
project(HarmonicMap)

if (NOT MSVC)
    set(CMAKE_CXX_FLAGS "-fpermissive -std=c++11")
    set(CMAKE_BUILD_TYPE DEBUG)
endif(NOT MSVC)


# Find MeshLib
find_package(MeshLib REQUIRED HINTS "${CMAKE_SOURCE_DIR}/3rdparty")
if (NOT MeshLib_FOUND)
    message(FATAL_ERROR "MeshLib Not Found!")
endif (NOT MeshLib_FOUND)


# Add module
add_subdirectory("harmonic_map")
