// #define NOMINMAX
// #include <Windows.h>
// #undef NOMINMAX

#include "typedefs.h"
#include "utils.h"
#include "modules.h"

#include <pcl/io/vtk_lib_io.h>
#include <pcl/io/ply_io.h>

#include <pcl/common/transforms.h>
#include <pcl/visualization/pcl_visualizer.h>
#include <pcl/point_types_conversion.h >

#include <queue>

bool getHeatMapColor(float value, float *red, float *green, float *blue)
{
	const int NUM_COLORS = 4;
	static float color[NUM_COLORS][3] = {{0, 0, 1}, {0, 1, 0}, {1, 1, 0}, {1, 0, 0}};
	// A static array of 4 colors:  (blue,   green,  yellow,  red) using {r,g,b} for each.

	int idx1;				// |-- Our desired color will be between these two indexes in "color".
	int idx2;				// |
	float fractBetween = 0; // Fraction between "idx1" and "idx2" where our value is.

	if (value <= 0)
	{
		idx1 = idx2 = 0;
	} // accounts for an input <=0
	else if (value >= 1)
	{
		idx1 = idx2 = NUM_COLORS - 1;
	} // accounts for an input >=0
	else
	{
		value = value * (NUM_COLORS - 1);	// Will multiply value by 3.
		idx1 = floor(value);				// Our desired color will be after this index.
		idx2 = idx1 + 1;					// ... and before this index (inclusive).
		fractBetween = value - float(idx1); // Distance between the two indexes (0-1).
	}

	*red = (color[idx2][0] - color[idx1][0]) * fractBetween + color[idx1][0];
	*green = (color[idx2][1] - color[idx1][1]) * fractBetween + color[idx1][1];
	*blue = (color[idx2][2] - color[idx1][2]) * fractBetween + color[idx1][2];

	return true;
}

int main(int argc, char **argv)
{
	std::string file_name = "config.txt";

	readConfigFile(file_name);
	// makeResultFolder(g_RESULT_DIR);

	// ---------------------------------------------------------generate file's datapath
	std::string file_final_pose_matrix = g_RESULT_DIR + "pose_result_kitti.txt";
	std::string file_Ransac_delta_matrix = g_RESULT_DIR + "ransac_delta.txt";
	std::string file_ICP_delta_matrix = g_RESULT_DIR + "icp_delta.txt";
	std::string file_approx_ops_counter = g_RESULT_DIR + "approx_search_ops.txt";
	std::string file_approx_lf_counter = g_RESULT_DIR + "leader_follower_num.txt";

	// ---------------------------------------------------------define variables
	int index_start = 0;
	std::queue<FeatureCloud> clouds;
	std::vector<std::string> path2bins;
	std::vector<int> approx_lf_counter;
	std::vector<int> approx_ops_counter;

	// initialized identity matrix
	Eigen::Matrix4f final_result_kitti = Eigen::Matrix4f::Identity();
	// matrix
	std::ofstream stream_icp_matrix;
	std::ofstream stream_ransac_matrix;
	std::ofstream stream_final_pose_matrix;
	// vector
	std::ofstream stream_approx_lf;
	std::ofstream stream_approx_ops;
	// loadBINFile(path2bins[n], cloud_);

	// The color we will be using
	float bckgr_gray_level = 0.0; // Black
	float txt_gray_lvl = 1.0 - bckgr_gray_level;

	PointCloud::Ptr cloud_in(new PointCloud);  // Original point cloud
	PointCloud::Ptr cloud_in2(new PointCloud); // Original point cloud

	PointCloud::Ptr cloud_tr(new PointCloud);  // Transformed point cloud
	PointCloud::Ptr cloud_icp(new PointCloud); // ICP output point cloud

	pcl::TextureMesh mesh;
	FeatureCloud cloud_;

	// --------------Stage1: Loading Frames--------------

	// std::cout << "Scene Point cloud size : " << std::endl;
	cout << "loading 1st cloud... " << endl;

	if (pcl::io::loadPolygonFileOBJ(argv[1], mesh) < 0)
	{
		PCL_ERROR("Error loading cloud %s.\n", argv[1]);
		return (-1);
	}

	cout << "loaded " << endl;

	pcl::fromPCLPointCloud2(mesh.cloud, *cloud_in);

	cloud_.setInputCloud(cloud_in);
	clouds.push(cloud_);
	cout << "Scene Point cloud size : " << cloud_in->points.size() << endl;

	cout << "loading 2nd cloud... " << endl;

	if (pcl::io::loadPolygonFileOBJ(argv[2], mesh) < 0)
	{
		PCL_ERROR("Error loading cloud %s.\n", argv[1]);
		return (-1);
	}

	cout << "loaded " << endl;

	pcl::fromPCLPointCloud2(mesh.cloud, *cloud_in2);

	cloud_.setInputCloud(cloud_in2);
	clouds.push(cloud_);

	cout << "Scene Point cloud size : " << cloud_in2->points.size() << endl;

	// --------------Stage2: Preprocessing--------------
	cout << "Preprocessing... " << endl;

	// filter(clouds.back());
	downSample(clouds.back(), 0.01);

	// filter(clouds.front());
	downSample(clouds.front(), 0.01);

	// --------------Stage3: Normal Calculation--------------
	cout << "Computing Normals... " << endl;

	computeSurfaceNormals(clouds.back(), approx_lf_counter, approx_ops_counter);
	computeSurfaceNormals(clouds.front(), approx_lf_counter, approx_ops_counter);

	// --------------Stage4: Key Points Detection--------------

	detectKeyPoints(clouds.back());
	detectKeyPoints(clouds.front());

	if (argc > 3 && strcmp(argv[3], "-show_kpt") == 0)
	{

		pcl::visualization::PCLVisualizer Key_viewer("Key Points");
		int v1(0);
		int v2(1);

		Key_viewer.createViewPort(0.0, 0.0, 0.5, 1.0, v1);
		Key_viewer.createViewPort(0.5, 0.0, 1.0, 1.0, v2);

		pcl::visualization::PointCloudColorHandlerCustom<PointT> cloud_tr_color_h(clouds.front().getPointCloud(), 20, 180, 20);
		Key_viewer.addPointCloud(clouds.front().getPointCloud(), cloud_tr_color_h, "cloud_in_v1", v1);

		pcl::visualization::PointCloudColorHandlerCustom<PointT> cloud_in_color_h(clouds.back().getPointCloud(), (int)255 * txt_gray_lvl, (int)255 * txt_gray_lvl, (int)255 * txt_gray_lvl);
		Key_viewer.addPointCloud(clouds.back().getPointCloud(), cloud_in_color_h, "cloud_in_v2", v2);

		pcl::visualization::PointCloudColorHandlerCustom<pcl::PointXYZ> keypoints_color_handler_v1(clouds.front().getKeyPoints(), 255, 0, 0);
		Key_viewer.addPointCloud(clouds.front().getKeyPoints(), keypoints_color_handler_v1, "key_points_v1", v1);
		Key_viewer.setPointCloudRenderingProperties(pcl::visualization::PCL_VISUALIZER_POINT_SIZE, 7, "key_points_v1");
		pcl::visualization::PointCloudColorHandlerCustom<pcl::PointXYZ> keypoints_color_handler_v2(clouds.back().getKeyPoints(), 255, 0, 0);
		Key_viewer.addPointCloud(clouds.back().getKeyPoints(), keypoints_color_handler_v2, "key_points_v2", v2);
		Key_viewer.setPointCloudRenderingProperties(pcl::visualization::PCL_VISUALIZER_POINT_SIZE, 7, "key_points_v2");

		while (!Key_viewer.wasStopped())
		{
			Key_viewer.spinOnce();
		}
	}

	// --------------Stage5: Feature Description--------------
	describeFeatures(clouds.back());
	describeFeatures(clouds.front());

	cout << "Feature estimated. " << endl;

	// -------------Stage6: Correspondence Estimation--------------
	Correspondences all_correspondences;
	Correspondences inliers;

	cout << "Estimating Correspondence..." << endl;

	estimateCorrespondence((clouds.back()), (clouds.front()), all_correspondences); // (source, target)

	cout << "Done." << endl;

	// ------------Stage7: Corresponence Rejection--------------
	Result *init_result_ptr, init_result;
	init_result_ptr = &init_result;

	rejectCorrespondences((clouds.back()), (clouds.front()),
						  all_correspondences, inliers, init_result_ptr); // (source, target)

	/** Constructing PointNormal **/
	constructPointNormal(clouds.back(), clouds.front());

	// -----------Stage8: Pose Estimation (ICP)--------------
	Result *icp_result_ptr, icp_result;
	icp_result_ptr = &icp_result;

	iterativeClosestPoints((clouds.back()), (clouds.front()), icp_result_ptr,
						   inliers, approx_lf_counter, approx_ops_counter);

	cout << "ICP terminated." << endl;

	Eigen::Matrix4f final_result = icp_result_ptr->final_transformation * init_result_ptr->final_transformation;
	// final_result_kitti = final_result_kitti * final_result;

	// cout << "results saved." << endl;

	printMatrix("ICP", icp_result_ptr->final_transformation);
	printMatrix("Final Pose", final_result);

	std::string s_Path = "source.ply";
	std::string t_Path = "target.ply";
	std::string icp_Path = "icp.ply";
	pcl::io::savePLYFileBinary(s_Path, *clouds.back().getPointCloud());
	pcl::io::savePLYFileBinary(t_Path, *clouds.front().getPointCloud());

	pcl::visualization::PCLVisualizer viewer("ICP registration");

	// Create two vertically separated viewports
	int v1(0);
	int v2(1);
	int v3(2);
	viewer.createViewPort(0.0, 0.0, 0.33, 1.0, v1);
	viewer.createViewPort(0.33, 0.0, 0.67, 1.0, v2);
	viewer.createViewPort(0.67, 0.0, 1.0, 1.0, v3);

	// Source point cloud is white
	pcl::visualization::PointCloudColorHandlerCustom<PointT> cloud_in_color_h(clouds.back().getPointCloud(), (int)255 * txt_gray_lvl, (int)255 * txt_gray_lvl, (int)255 * txt_gray_lvl);
	viewer.addPointCloud(clouds.back().getPointCloud(), cloud_in_color_h, "cloud_in_v1", v1);

	// Target point cloud is green
	pcl::visualization::PointCloudColorHandlerCustom<PointT> cloud_tr_color_h(clouds.front().getPointCloud(), 20, 180, 20);
	viewer.addPointCloud(clouds.front().getPointCloud(), cloud_tr_color_h, "cloud_tr_v1", v1);
	viewer.addPointCloud(clouds.front().getPointCloud(), cloud_tr_color_h, "cloud_in_v2", v2);

	pcl::transformPointCloud(*(clouds.back().getPointCloud()), *cloud_icp, final_result);
	pcl::io::savePLYFileBinary(icp_Path, *cloud_icp);

	// ICP aligned point cloud is red
	pcl::visualization::PointCloudColorHandlerCustom<PointT> cloud_icp_color_h(cloud_icp, 180, 20, 20);
	viewer.addPointCloud(cloud_icp, cloud_icp_color_h, "cloud_icp_v2", v2);

	// Set background color
	viewer.setBackgroundColor(bckgr_gray_level, bckgr_gray_level, bckgr_gray_level, v1);
	viewer.setBackgroundColor(bckgr_gray_level, bckgr_gray_level, bckgr_gray_level, v2);
	viewer.setBackgroundColor(bckgr_gray_level, bckgr_gray_level, bckgr_gray_level, v3);

	pcl::PointXYZ searchPoint;
	pcl::PointXYZ target_p;

	float radius = 0.03;
	std::vector<int> pointIdxRadiusSearch;
	std::vector<float> pointRadiusSquaredDistance;

	pcl::KdTreeFLANN<pcl::PointXYZ> kdtree;
	kdtree.setInputCloud(cloud_icp);

	float max_d = -999;
	float min_d = 999;
	float d = 0;
	std::vector<float> distances;

	for (int indx = 0; indx < clouds.front().getPointCloud()->points.size(); indx++)
	{

		// std::cout << "Searching... " << std::endl;

		searchPoint.x = clouds.front().getPointCloud()->points[indx].x;
		searchPoint.y = clouds.front().getPointCloud()->points[indx].y;
		searchPoint.z = clouds.front().getPointCloud()->points[indx].z;

		if (kdtree.radiusSearch(searchPoint, radius, pointIdxRadiusSearch, pointRadiusSquaredDistance) > 10)
		{

			target_p.x = 0;
			target_p.y = 0;
			target_p.z = 0;

			for (std::size_t i = 0; i < pointIdxRadiusSearch.size(); ++i)
			{

				target_p.x += (*cloud_icp)[pointIdxRadiusSearch[i]].x;
				target_p.y += (*cloud_icp)[pointIdxRadiusSearch[i]].y;
				target_p.z += (*cloud_icp)[pointIdxRadiusSearch[i]].z;
			}

			target_p.x /= pointIdxRadiusSearch.size();
			target_p.y /= pointIdxRadiusSearch.size();
			target_p.z /= pointIdxRadiusSearch.size();

			d = pcl::squaredEuclideanDistance(target_p, searchPoint);

			distances.push_back(d);

			if (d > max_d)
				max_d = d;
			if (d < min_d)
				min_d = d;
		}
		else
		{
			distances.push_back(0.0);
		}
	}

	std::cout << "size " << distances.size() << std::endl;
	std::cout << "max_dist " << max_d << std::endl;

	PointCloudRGB::Ptr cloud_heatmap(new PointCloudRGB);
	// PointHSV HSV;
	PointRGB RGB;
	float r, g, b;

	float color_max = -999;
	for (int indx = 0; indx < clouds.front().getPointCloud()->points.size(); indx++)
	{

		d = distances[indx];
		if (d > 0.90 * max_d)
			d = 0;
		if (d > color_max)
			color_max = d;
	}

	for (int indx = 0; indx < clouds.front().getPointCloud()->points.size(); indx++)
	{

		d = distances[indx];

		RGB.x = clouds.front().getPointCloud()->points[indx].x;
		RGB.y = clouds.front().getPointCloud()->points[indx].y;
		RGB.z = clouds.front().getPointCloud()->points[indx].z;

		getHeatMapColor((d / color_max), &r, &g, &b);

		RGB.r = r * 255.0;
		RGB.g = g * 255.0;
		RGB.b = b * 255.0;

		cloud_heatmap->push_back(RGB);
	}

	std::cout << "num_points: " << cloud_heatmap->points.size() << std::endl;

	pcl::visualization::PointCloudColorHandlerRGBField<PointRGB> rgb(cloud_heatmap);
	viewer.addPointCloud(cloud_heatmap, rgb, "cloud_heatmap", v3);

	std::string writePath = "Heat_map.ply";
	pcl::io::savePLYFileBinary(writePath, *cloud_heatmap);

	while (!viewer.wasStopped())
	{
		viewer.spinOnce();
	}

	return 0;
}
