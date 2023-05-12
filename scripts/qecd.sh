
for s in data/boundary/*source.obj; do
    filename=$(basename -- "$s")
    fname=${filename%.*}
    kp="data/keypoints/$fname.txt"
    mp="data/metrics/$fname.txt"
    # echo -e "$kp | $mp"
    echo -e "Running $kp | $mp"
    python3 quadric_edge_collapse_decimation/qecd.py $s $kp $mp
done
echo
for t in data/boundary/*target.obj; do
    # echo $t
    filename=$(basename -- "$t")
    fname=${filename%.*}
    kp="data/keypoints/$fname.txt"
    mp="data/metrics/$fname.txt"
    echo -e "Running $kp | $mp"
    python3 quadric_edge_collapse_decimation/qecd.py $t $kp $mp
done

