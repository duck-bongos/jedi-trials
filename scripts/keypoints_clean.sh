if [ -d data/collapsed ]
then
    echo -e "Cleaning data/keypoints..."
    rm -rf data/keypoints/*.txt
    echo -e "Cleaned data/keypoints..."
fi