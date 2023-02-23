#include <iostream>
#include <pcl/io/pcd_io.h>
#include <pcl/point_types.h>

using namespace std;

int main() {
	pcl::PointCloud<pcl::PointXYZ> cloud;

	cloud.width = 5;
	cloud.height = 1;
	cloud.is_dense = false;
	cloud.resize(cloud.width * cloud.height);

	for (auto& point: cloud)
	{
		point.x = 1024 * rand () / (RAND_MAX + 1.0f);
		point.y = 1024 * rand () / (RAND_MAX + 1.0f);
		point.z = 1024 * rand () / (RAND_MAX + 1.0f);
	}

	pcl::io::savePCDFileASCII ("../data/test.pcd", cloud);
	cerr << "Saved " << cloud.size() << " data points to test.pcd." << endl;

	for (const auto& point: cloud)
		cerr << "    " << point.x << " " << point.y << " " << point.z << endl;

	return 0;
}