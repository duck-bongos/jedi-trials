cd optimization/HarmonicMap

# enter the build directory
cd build
cmake ..
cmake --build .

# return to HarmonicMap
cd ..

# check the bin directory for the executable.
# The executable name is the same as in line 22 of
# optimization/HarmonicMap/harmonic_map/CMakeLists.txt
if [ ! -f bin/map ]
then
    echo -e "executable doesn't exist. Please check the CMakeLists.txt and the build.\n\n"
    exit 1
fi

# echo -e 'Mapping source...'
bin/map ../../data/annotated/source/masked_source_object.obj ../../data/optimized/mapped_source.obj

# echo -e 'Mapping target...'
bin/map ../../data/annotated/target/masked_target_object.obj ../../data/optimized/mapped_target.obj


# return to the top level directory
cd ../..
