#include <iostream>
#include <fstream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <limits>
#include <sstream>
#include <string>
#include <map>

using namespace std;

struct Point {
  double x, y, z;
  Point(double x, double y, double z) : x(x), y(y), z(z) {}
  double distanceTo(const Point& other) const {
    double dx = x - other.x;
    double dy = y - other.y;
    double dz = z - other.z;
    return sqrt(dx*dx + dy*dy + dz*dz);
  }
};

map<string, int> get_points(string fname) {
    map<string, int> pts;
    string name;
    int vert_id;
    string line;
    ifstream infile(fname);
    while (getline(infile, line)) {
        istringstream iss(line);
        if (!(iss >> name >> vert_id)) { break;}
        pts[name] = vert_id;
    }

    return pts;
}


vector<Point> readPointCloud(const char* filename) {
    std::ifstream file(filename);
    
    if (!file.is_open()) {
        std::cerr << "Failed to open file" << std::endl;
    }
    
    std::vector<Point> points;
    std::string line;
    
    while (std::getline(file, line)) {
        if (line.substr(0, 2) == "v ") {
            std::stringstream ss(line.substr(2));
            double u, v, z;
            ss >> u >> v >> z;
            Point p = Point(u, v, z );
            points.push_back(p);
        }
    }
    file.close();
    return points;
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

string change_mpath(string fname) {
  string mname = replace_substr(fname, "transformed", "statistics");
  mname = replace_substr(mname, "source.obj", "stats.txt");
  return mname;
}

void write_map(
  string fname, 
  vector<Point> source, 
  vector<Point> target
) {
    string nname = change_fpath(fname);
    ofstream outfile(nname);
    double dist;
    // Perform K-Nearest Neighbors between the source and target point clouds.
    int k = 1; // set k to 1 for nearest neighbor search
    cout << "Writing non-rigid mapping from source to target..." << endl;
    for (int i = 0; i < source.size(); i++) {
      int nearestIndex = nearestNeighbor(source[i], target);
      outfile << i << " " << nearestIndex << endl;
    }
    cout << "Wrote out non-rigid mapping from source to target." << endl;
}

void calculate_metrics(  
  string fname, 
  vector<Point> source, 
  vector<Point> target, 
  map<string, int> source_points, 
  map<string, int> target_points
) {
  // if both
  string mname = change_mpath(fname);
  cout << mname << endl;
  ofstream metrics(mname);

  metrics << "Name SourceId TargetId Error" << endl;
  double total_distance = 0.0;
  for (auto k: source_points ) {
    string key = k.first;
    int idx = k.second;
    int target_idx = target_points[key];

    Point s = source[idx];
    Point t = target[target_idx];

    // calculate the Euclidean norm
    double dist = s.distanceTo(t);
    total_distance += dist;
    cout << key << " " << idx << " " << target_idx << " " << dist << endl;

    // write out metrics to file
    metrics << key << " " << idx << " " << target_idx << " " << dist << endl;
  }
  // write out Sum of Squared Errors
  metrics << "\n-------------------------------------" << endl;
  metrics << "Sum of Error" << endl;
  metrics << total_distance << endl;
}

int main(int argc, char** argv) {
  if (argc != 5) {
    cerr << "Usage: knn <source.obj> <target.obj> <source_points.txt> <target_points.txt>" << endl;
    return 1;
  }
  map<string, int> s_metrics = get_points(argv[3]);
  map<string, int> t_metrics = get_points(argv[4]);

  // Read the source and target point clouds.
  vector<Point> sourcePoints = readPointCloud(argv[1]);
  vector<Point> targetPoints = readPointCloud(argv[2]);

  calculate_metrics(argv[1], sourcePoints, targetPoints, s_metrics, t_metrics);

  write_map(argv[1], sourcePoints, targetPoints);

  return 0;
}

/*
breakpoint set --file nrr.cc --line 54
breakpoint set --file nrr.cc --line 162
breakpoint set --file nrr.cc --line 138

*/