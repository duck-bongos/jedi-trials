# if the data directory is at the same level, clean it
if [[ -d "data" ]]
then 
	echo "data directory exists. Removing texture and voxel files"
	rm -rf data/*.txt
	echo "Texture and voxel files have been removed."
	echo "Looking to clean up data/boundary directory..."
	if [[ -d "data/boundary" ]]
	then
		echo "data/boundary exists, cleaning..."
		rm -rf data/boundary/*.obj
		echo "Removed .obj files from data/boundary."
	fi

	if [[ -d "data/metrics" ]]
	then
		echo "Removing metric files"
		rm -rf data/metrics/*.txt
	fi

	if [[ -d "data/keypoints" ]]
	then
		echo "Removing Keypoints"
		rm -rf data/keypoints/*.txt
	fi
fi



