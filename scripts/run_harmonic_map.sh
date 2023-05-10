

# check the bin directory for the executable.
# The executable name is the same as in line 22 of
# optimization/HarmonicMap/harmonic_map/CMakeLists.txt
if [[ ! -f HarmonicMap/bin/map ]]
then
    echo -e "executable doesn't exist. Building...\n"
    cd HarmonicMap

    # enter the build directory
    cd build
    cmake ..
    cmake --build .

    # return to optimization/HarmonicMap
    echo -e "Built bin/map\n"
    cd ..

    echo "==============================="
    echo $PWD
    echo "==============================="
fi


if [[ ! -f HarmonicMap/bin/map ]]
then
    echo "$PWD"
    echo -e "Executable bin/map doesn't exist. Please check the CMakeLists.txt and the build.\n\n"
    exit 1
fi

sleep 1
cd HarmonicMap

echo -e 'Mapping source...'
for f in ../data/collapsed/*source.obj; do 
    echo "Mapping $f"
    bin/map $f ../data/mapped/$(basename -- $f) 
done

# bin/map ../data/collapsed/source.obj ../data/mapped/source.obj
# python3 hm.py ../data/mapped/source.obj
# bin/map ../../data/source/source.obj ../../data/optimized/mapped_source.obj

echo -e 'Mapping target...'
for f in ../data/collapsed/*target.obj; do
    echo "Mapping $f"
    bin/map $f ../data/mapped/$(basename -- $f)
done

# bin/map ../data/collapsed/target.obj ../data/mapped/target.obj
# python3 hm.py ../data/mapped/target.obj
# bin/map ../../data/target/target.obj ../../data/optimized/mapped_target.obj

# GNU Parallel
# parallel --link bin/map ::: ../../data/annotated/source/masked_source_object.obj ../../data/source/source.obj ../../data/annotated/target/masked_target_object.obj ../../data/target/target.obj ::: ../../data/optimized/mapped_masked_source.obj ../../data/optimized/mapped_source.obj ../../data/optimized/mapped_masked_target.obj ../../data/optimized/mapped_target.obj

# return to the top level directory
cd ..

echo "Returned to $PWD"
