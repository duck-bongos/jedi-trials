

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
touch erring_files.txt
for s in ../data/collapsed/*source.obj; do
    filename=$(basename -- "$s")
    mname="../data/mapped/$filename"
    echo "Running Harmonic Map on $s -> $mname"
    gtimeout 60 bin/map $s $mname > tmp.txt
    if [[ "$(tail -1 tmp.txt | cut -c-8)" == "Wrote to" ]]; then
        python3 hm.py $mname
    else
        echo "$s\n" >> erring_files.txt
    fi
done

for s in ../data/collapsed/*target.obj; do
    filename=$(basename -- "$s")
    mname="../data/mapped/$filename"
    echo "Running Harmonic Map on $s -> $mname"
    gtimeout 60 bin/map $s $mname > tmp.txt
    if [[ "$(tail -1 tmp.txt | cut -c-8)" == "Wrote to" ]]; then
        python3 hm.py $mname
    else
        echo "$s\n" >> erring_files.txt
    fi
done
if [[ ! -s erring_files.txt ]]; then
    mv erring_files.txt ../data/statistics
fi

rm tmp.txt

cd ..

echo "Returned to $PWD"
