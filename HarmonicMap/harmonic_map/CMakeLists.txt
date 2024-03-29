project(HarmonicMap)

if(APPLE)
  add_definitions(-DMAC_OS)
endif(APPLE)

# Include the 'include' of the project itself
include_directories("include")

# Include MeshLib core and Eigen in 3rdparty
include_directories("${MeshLib_DIR}/core"
                    "${CMAKE_SOURCE_DIR}/3rdparty/eigen")

# Also, the file(GLOB...) allows for wildcard additions
file(GLOB SRCS
    "include/*.h"
    "src/*.cpp"
    "src/*.cc")

# Add an executable target called harmonic_map to be built from 
# the source files.
add_executable(map ${SRCS})


# Install the executeable program in the bin folder of the
# current project directory.
add_custom_command(
    TARGET map
    POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E 
    copy $<TARGET_FILE:map> ${CMAKE_SOURCE_DIR}/bin
  )