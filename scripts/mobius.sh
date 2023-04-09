if [ ! -f mobius/mobius ]
then
    echo -e "Executable mobius/mobius doesn't exist. Building..."
    clang++ -std=c++11 mobius/mobius.cc -o mobius/mobius
    echo -e "Built executable mobius/mobius."

fi

mobius/mobius data/mapped/source.obj data/keypoints/source.txt
mobius/mobius data/mapped/target.obj data/keypoints/target.txt
