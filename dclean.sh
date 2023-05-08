cd /Users/dan/Dropbox/SBU/spring_2023/thesis/data
for dir in */; do
    if [[ -f "$dir/data.zip" ]]
    then
        rm -rf "$dir/data.zip"
    fi
    if [[ -d "$dir/data/" ]]
    then
        rm -rf "$dir/data/"
    fi
done

cd -