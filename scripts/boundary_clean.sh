# if the data directory is at the same level, clean it
if [ -d "data" ]
then 
	echo "data directory exists. checking for data/annotated."
	
	if [ -d "data/annotated" ]
	then
		echo "data/annotated directory exists. checking for data/annotated/source."
	
		if [ -d "data/annotated/source" ]
		then
			echo "data/annotated/source directory exists. Cleaning..."
			rm -rf data/annotated/source/*
			echo "data/annotated/source is now empty."
		fi

		if [ -d "data/annotated/target" ]
		then
			echo "data/annotated/target directory exists. Cleaning..."
			rm -rf data/annotated/target/*
			echo "data/annotated/source is now empty."
		fi
	fi
fi


# remove everything from the 

