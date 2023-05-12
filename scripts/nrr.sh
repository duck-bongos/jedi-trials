if [[ ! -f non_rigid_registration/nrr ]]
then
    clang++ -std=c++11 non_rigid_registration/nrr.cc -o non_rigid_registration/nrr
fi

dm="data/metrics/"
for s in data/transformed/*source.obj; do
    sname=$(basename -- "$s")
    fsname=${sname%.*}
    s_abbr=$(echo "$fsname" | cut -d '_' -f 3 )
    s_abbr_=$(echo "$fsname" | cut -d '_' -f 2 )
    s_abbr__=$(echo "$fsname" | cut -d '_' -f 1 )

    for t in data/transformed/*target.obj; do
        tname=$(basename -- "$t")
        ftname=${tname%.*}
        t_abbr=$(echo $ftname | cut -d '_' -f 1 )
        if [[ "$t_abbr" == "$s_abbr" ]]; then
            echo "$dm$fsname $dm$ftname"
            non_rigid_registration/nrr $s $t $dm$fsname.txt $dm$ftname.txt

        elif [[ "$t_abbr" == "$s_abbr_" ]]; then
            echo "$dm$fsname $dm$ftname"
            non_rigid_registration/nrr $s $t $dm$fsname.txt $dm$ftname.txt

        elif [[ "$t_abbr" == "$s_abbr__" ]]; then
            echo "$dm$fsname $dm$ftname"
            non_rigid_registration/nrr $s $t $dm$fsname.txt $dm$ftname.txt
        fi
    done
done
