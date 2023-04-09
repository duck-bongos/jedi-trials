if [ ! -f non_rigid_registration/nrr ]
then
    clang++ -std=c++11 non_rigid_registration/nrr.cc -o non_rigid_registration/nrr
fi

non_rigid_registration/nrr data/transformed/source.obj data/transformed/target.obj