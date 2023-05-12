cd boundary_detection

# run all the full boundary examples
echo "Running consistent boundary examples..."
for b in boundaries/*.txt; do
    echo $b
    python3 main.py -i ../data/source.png -o ../data/source.obj -b $b
    python3 main.py -i ../data/target.png -o ../data/target.obj -b $b
done
echo "Completed consistent boundary examples."
echo; echo
echo "Running inconsistent boundary examples..."
for b in boundaries/*.txt; do
    bb="$(basename -- "$b")"
    bx="${bb%.*}"
    for s in inconsistent_boundaries/*; do
        basename="$(basename "$s")"
        if [[ "$basename" == "$bx" ]]; then
            for c in $s/*.txt; do
                python3 main.py -i ../data/source.png -o ../data/source.obj -b $b -c $c
            done
        fi
    done
done
echo "Completed inconsistent boundary examples."

cd -