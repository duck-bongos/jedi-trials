#include <iostream>
#include <fstream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <limits>
#include <sstream>
#include <string>

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

string replace_substr(const string& str, const string& old_substr, const string& new_substr) {
    string result = str;
    size_t pos = result.find(old_substr);
    if (pos != string::npos) {
        result.replace(pos, old_substr.length(), new_substr);
    }
    return result;
}

string change_fpath(string fname) {
    string nname = replace_substr(fname, "transformed", "registration");
    nname = replace_substr(nname, "source.obj", "map.txt");
    return nname;
}

void write_map(string fname, vector<Point> source, vector<Point> target) {
    string nname = change_fpath(fname);
    ofstream outfile(nname);
    // Perform K-Nearest Neighbors between the source and target point clouds.
    int k = 1; // set k to 1 for nearest neighbor search
    cout << "Writing non-rigid mapping from source to target..." << endl;
    for (int i = 0; i < source.size(); i++) {
      int nearestIndex = nearestNeighbor(source[i], target);
      outfile << i << " " << nearestIndex << endl;

    }
    cout << "Wrote out non-rigid mapping from source to target." << endl;
}


int main(int argc, char** argv) {
  if (argc != 3) {
    cerr << "Usage: knn <source.obj> <target.obj>" << endl;
    return 1;
  }

  // Read the source and target point clouds.
  vector<Point> sourcePoints = readPointCloud(argv[1]);
  vector<Point> targetPoints = readPointCloud(argv[2]);

  write_map(argv[1], sourcePoints, targetPoints);

  return 0;
}
