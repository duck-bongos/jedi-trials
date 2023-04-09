if [ ! -f HarmonicMap/bin/map ]
then
    echo -e "executable doesn't exist. Building...\n"
    cd HarmonicMap

    # enter the build directory
    cd build
    cmake ..
    cmake --build .

    # return to optimization/HarmonicMap
    echo -e "Built HarmonicMap/bin/map\n"
    cd ../..

    echo $PWD

fi

if [ ! -f non_rigid_registration/nrr ]
then
    clang++ -std=c++11 non_rigid_registration/nrr.cc -o non_rigid_registration/nrr
    echo -e "Built non_rigid_registration/nrr"
fi

if [ ! -f mobius/mobius ]
then
    clang++ -std=c++11 mobius/mobius.cc -o mobius/mobius
    echo -e "Built mobius/mobius"
fi
