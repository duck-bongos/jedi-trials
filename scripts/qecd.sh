if [[ -z $1 ]]
then
    python3 quadric_edge_collapse_decimation/qecd.py data/boundary/source.obj
    python3 quadric_edge_collapse_decimation/qecd.py data/boundary/target.obj
else
    python3 quadric_edge_collapse_decimation/qecd.py data/source.obj data/
    python3 quadric_edge_collapse_decimation/qecd.py data/target.obj data/
fi