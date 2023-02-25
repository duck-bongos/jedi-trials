cmake_minimum_required(VERSION 3.5 FATAL_ERROR)
project(pcd_write)
find_package(PCL 1.3 REQUIRED)

include_directories(${PCL_INCLUDE_DIRS})
link_directories(${PCL_LIBRARY_DIRS} mediapipe)
add_definitions(${PCL_DEFINITIONS})


# designate executables
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/bin)

# add executable 
add_executable(pcd_write src/pcd_write.cc)
target_link_libraries(pcd_write ${PCL_LIBRARIES} mediapipe)