# if the data directory is at the same level, clean it
if [ -d "data" ]
then 
	echo "data directory exists. Removing texture and voxel files"
	rm -rf data/*.txt
	echo "Texture and voxel files have been removed.\n"
	echo "Looking to clean up data/boundary directory..."
	if [ -d "data/boundary" ]
	then
		echo "data/boundary exists, cleaning..."
		rm -rf data/boundary/*
		echo "data/boundary is now empty."
	fi
fi


