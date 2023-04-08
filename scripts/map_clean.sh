# starting from top level directory

# clean the data/optimized directory
rm -rf data/mapped/*

# clean the build and bin
cd HarmonicMap/

echo "removing ./bin contents..."
rm -rf bin/*
echo "removed ./bin contents."

echo "removing ./build contents..."
rm -rf build/*
echo "removed ./build contents..."


cd ..
echo "Returned to $PWD"