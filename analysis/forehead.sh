pd () {
    parent_dir="../../data"
    for person_dir in "$parent_dir"/*/; do
        # Get the name of the person from the subdirectory name
        person=$(basename "$person_dir")
        if [[ "$person" != "self" ]]; then
            # Loop through each file in the person subdirectory
            for dir in "$person_dir"statistics/data/statistics/*; do
                echo "$dir" | grep "center"

            done
        fi
    done
}

pd