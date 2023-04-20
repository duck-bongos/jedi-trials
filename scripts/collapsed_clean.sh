if [[ -d data/collapsed ]]
then
    echo -e "Cleaning data/collapsed..."
    rm -rf data/collapsed/*.obj
    rm -rf data/collapsed/*.mtl
    echo -e "Cleaned data/collapsed..."
fi