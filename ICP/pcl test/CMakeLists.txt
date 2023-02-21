cmake_minimum_required(VERSION 2.8 FATAL_ERROR)

project(jedi_trials)

# should be set in environment variables
set(PCL_DIR C:/Users/dan/Desktop/PCL-1.12.1/cmake -Wno-dev)
set(PCL_ROOT C:/Users/dan/Desktop/PCL-1.12.1/cmake -Wno-dev)

message("The value of PCL_ROOT is ${PCL_ROOT}")

# find_package(PCL 1.12.1 EXACT REQUIRED PATHS ./PCL-1.12.1/include/pcl-1.12)
find_package(PCL 1.12.1 EXACT REQUIRED PATHS C:/Users/dan/Desktop/PCL-1.12.1/cmake)

include_directories(${PCL_INCLUDE_DIRS} include)

link_directories(${PCL_LIBRARY_DIRS})

add_definitions(${PCL_DEFINITIONS} -O3 -DNDEBUG -DPCL_NO_PRECOMPILE)
# add_definitions(${PCL_DEFINITIONS})

# add_executable (cloud_viewer cloud_viewer.cpp)
add_executable (pc_pipeline src/modules.cpp src/utils.cpp src/read_config.cpp src/pc_pipeline.cpp)

target_link_libraries (pc_pipeline ${PCL_LIBRARIES})
# target_link_libraries (cloud_viewer ${PCL_LIBRARIES})

# $PATH_TO_PCLCONFIG: path to PCLConfig.cmake


#set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -O3 -DNDEBUG")


set_property(TARGET pc_pipeline PROPERTY CXX_STANDARD 11)

SET(EXECUTABLE_OUTPUT_PATH .././bin)