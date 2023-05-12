if [[ -f data/registration/map.txt ]]
then
    echo -e "Cleaning the data/registration directory..."
    rm -rf data/registration/map.txt
    rm -rf data/registration/*.txt
    echo -e "Cleaned the data/registration direcotry.\n"
fi