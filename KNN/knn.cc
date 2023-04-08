#include <iostream>
#include <fstream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <limits>
#include <sstream>

using namespace std;

struct Point {
  double x, y;
  Point(double x, double y) : x(x), y(y) {}
  double distanceTo(const Point& other) const {
    double dx = x - other.x;
    double dy = y - other.y;
    return sqrt(dx*dx + dy*dy);
  }
};

vector<Point> readPointCloud(const char* filename) {
    std::ifstream file(filename);
    
    if (!file.is_open()) {
        std::cerr << "Failed to open file" << std::endl;
    }
    
    std::vector<Point> texcoords;
    std::string line;
    
    while (std::getline(file, line)) {
        if (line.substr(0, 3) == "vt ") {
            std::stringstream ss(line.substr(3));
            float u, v;
            ss >> u >> v;
            Point p = Point(u, v);
            texcoords.push_back(p);
        }
    }
    
    file.close();
    return texcoords;
}

int nearestNeighbor(const Point& query, const vector<Point>& points) {
  int index = -1;
  double minDistance = numeric_limits<double>::infinity();
  for (int i = 0; i < points.size(); i++) {
    double distance = query.distanceTo(points[i]);
    if (distance < minDistance) {
      index = i;
      minDistance = distance;
    }
  }
  return index;
}

int main(int argc, char** argv) {
  if (argc != 3) {
    cerr << "Usage: knn <source.obj> <target.obj>" << endl;
    return 1;
  }

  // Read the source and target point clouds.
  vector<Point> sourcePoints = readPointCloud(argv[1]);
  vector<Point> targetPoints = readPointCloud(argv[2]);

  // Perform K-Nearest Neighbors between the source and target point clouds.
  int k = 1; // set k to 1 for nearest neighbor search
  for (int i = 0; i < sourcePoints.size(); i++) {
    int nearestIndex = nearestNeighbor(sourcePoints[i], targetPoints);
    cout << "Vertex " << i << " in source cloud maps to vertex " << nearestIndex
         << " in target cloud" << endl;
  }

  return 0;
}
