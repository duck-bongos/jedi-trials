#!/bin/bash

# for s in data/transformed/*source.obj; do
#     sname=$(basename -- "$s")
#     fsname=${sname%.*}
#     s_abbr=$(echo "$fsname" | cut -d '_' -f 3 )
#     s_abbr_=$(echo "$fsname" | cut -d '_' -f 2 )
#     s_abbr__=$(echo "$fsname" | cut -d '_' -f 1 )

#     for t in data/transformed/*target.obj; do
#         tname=$(basename -- "$t")
#         ftname=${tname%.*}
#         t_abbr=$(echo $ftname | cut -d '_' -f 1 )
#         if [[ "$t_abbr" == "$s_abbr" ]]; then
#             echo "$dm$fsname $dm$ftname"
            

#         elif [[ "$t_abbr" == "$s_abbr_" ]]; then
#             echo "$dm$fsname $dm$ftname"
            

#         elif [[ "$t_abbr" == "$s_abbr__" ]]; then
#             echo "$dm$fsname $dm$ftname"
#         fi
#     done
# done

float_finder () {
    grep -Eo '[0-9]+\.[0-9]+' $1 | tail -n 1
}


fufu () {
    grep -Eo '[0-9]+\.[0-9]+' $1
}
# moo() {
#     for f in "$1"/*; do
#         ff="$(basename $f)"
#         fff=${ff%.*}
#         echo $fff
#     done
# }

# munch() {
#     for pre in "outer" "middle" "inner" "custom"; do
#         for f in "$1"/*; do
#             ff="$(basename $f)"
#             fff=${ff%.*}
#             if [[ $pre"_stats" == "$fff" ]]; then
#                 echo $f > $pre"_norm.txt"
#             elif [[ *"$pre"* == $f ]]; then
#                 echo $f >> $pre"_ib.txt"
#             fi
#         done
#     done
# }

# yargh () {
#     if [[ *"$outer"* == "$1" ]]; then
#         echo "ya"
#     else
#         echo "na"
#     fi
# }

fx() {
    for pre in "outer" "middle" "inner" "custom"; do
        for file in "$1"/*.txt; do
            ff=$(basename -- "$file")
            fff=${ff%.*}

            # begins with
            if [[ "$fff" == $pre"_stats" ]]; then
                echo "$fff" > $pre"_cb.txt"
                float_finder $file >> $pre"_cb.txt"
            elif [[ "$fff" == "center_forehead_"$pre"_stats" ]]; then
                if [[ ! -f $pre"_ib.txt" ]]; then
                    touch $pre"_ib.txt"
                else
                    echo "$fff" > floats.txt
                    float_finder $file >> floats.txt                
                    paste floats.txt $pre"_ib.txt" > tmp.txt
                    mv tmp.txt $pre"_ib.txt"
                    cp $pre"_ib.txt" $pre"_suck.out"
                fi
            elif [[ "$file" == *"$pre"* ]]; then
                if [[ ! -f $pre"_ib.txt" ]]; then
                    touch $pre"_ib.txt"
                else
                    echo "$fff" > floats.txt
                    float_finder $file >> floats.txt                
                    paste floats.txt $pre"_ib.txt" > tmp.txt
                    mv tmp.txt $pre"_ib.txt"
                fi
            fi
        done
        # combine files
        if [[ ! -f $pre"_comb.psv" ]]; then
            paste  $pre"_cb.txt" $pre"_ib.txt" > $pre"_comb.psv"
        else
            paste  $pre"_cb.txt" $pre"_ib.txt" > tmp.psv
            echo "$pre"
            cat tmp.psv | sed '1d' >> $pre"_comb.psv"
        fi
    done
}

pd () {
    parent_dir="../../data"
    for person_dir in "$parent_dir"/*/; do
        # Get the name of the person from the subdirectory name
        person=$(basename "$person_dir")
        if [[ "$person" != "self" ]]; then
            # Loop through each file in the person subdirectory
            for dir in "$person_dir"statistics/data/statistics/; do
                echo "$dir"
            done
        fi
    done
}

fx $1