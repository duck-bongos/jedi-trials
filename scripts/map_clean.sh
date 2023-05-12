# starting from top level directory

# clean the data/optimized directory
rm -rf data/mapped/*.obj

# clean the build and bin
cd HarmonicMap/

echo "removing ./build contents..."
rm -rf build/*
echo "removed ./build contents..."

cd ..
echo "Returned to $PWD"