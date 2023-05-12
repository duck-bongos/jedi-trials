if [[ ! -f mobius/mobius ]]
then
    echo -e "Executable mobius/mobius doesn't exist. Building..."
    clang++ -std=c++11 mobius/mobius.cc -o mobius/mobius
    echo -e "Built executable mobius/mobius."
fi

for s in data/mapped/*source.obj; do
    filename=$(basename -- "$s")
    fname=${filename%.*}
    kp="data/keypoints/$fname.txt"
    echo "$s -> $kp"
    mobius/mobius $s $kp
done
echo
for t in data/mapped/*target.obj; do
    filename=$(basename -- "$t")
    fname=${filename%.*}
    kp="data/keypoints/$fname.txt"
    echo "$t -> $kp"
    mobius/mobius $t $kp
done

#mobius/mobius data/mapped/source.obj data/keypoints/source.txt
#mobius/mobius data/mapped/target.obj data/keypoints/target.txt
