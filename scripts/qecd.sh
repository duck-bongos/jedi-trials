# if [[ -z $1 ]]
# then
#     python3 quadric_edge_collapse_decimation/qecd.py data/boundary/source.obj
#     python3 quadric_edge_collapse_decimation/qecd.py data/boundary/target.obj
# else
#     python3 quadric_edge_collapse_decimation/qecd.py data/source.obj data/
#     python3 quadric_edge_collapse_decimation/qecd.py data/target.obj data/
# fi
for f in data/boundary/*source.obj; do
    echo "Running QECD on source obj $f"
    python3 quadric_edge_collapse_decimation/qecd.py $f;
done

for f in data/boundary/*target.obj; do
    echo "Running QECD on target obj $f"
    python3 quadric_edge_collapse_decimation/qecd.py $f;
done