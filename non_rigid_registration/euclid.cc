/*
Author: Dan Billmann

*/
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

struct M {
    vector<int> source;
    vector<int> target;
};

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

vector<Point> readPointCloud(const char* filename) {
    std::ifstream file(filename);
    
    if (!file.is_open()) {
        std::cerr << "Failed to open file" << std::endl;
    }
    
    std::vector<Point> texcoords;
    std::string line;
    
    while (std::getline(file, line)) {

        if (line.substr(0, 2) == "v ") {
            std::stringstream ss(line.substr(3));
            float u, v, z;
            ss >> u >> v >> z;
            Point p = Point(u, v, z);
            texcoords.push_back(p);
        }
    }
    file.close();
    return texcoords;
}

M readMap(string filename) {
    std::ifstream file(filename);

    if (!file.is_open()) {
        std::cerr << "Failed to open file" << std::endl;
    }
    
    vector<int> source;
    vector<int> target;

    std::string line;
    
    while (std::getline(file, line)) {
        std::stringstream ss(line);
        int u, v;
        ss >> u >> v;
        source.push_back(u);
        target.push_back(v);        
    }
    file.close();
    M m = {source, target};
    return m;
}

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

string replace_substr(
    const string& str, 
    const string& old_substr, 
    const string& new_substr
) {
    string result = str;
    size_t pos = result.find(old_substr);
    if (pos != string::npos) {
        result.replace(pos, old_substr.length(), new_substr);
    }
    return result;
}

string change_mpath(string fname) {
  string mname = replace_substr(fname, "transformed", "metrics");
  mname = replace_substr(mname, "source.obj", "metricsR3.txt");
  return mname;
}

void calculate_non_rigid_error(
    M nrr,
    vector<Point> source_points,
    vector<Point> target_points
) {
    int size = nrr.source.size();
    double total_distance = 0.0;
    double max_distance = 0.0;
    ofstream outfile("data/metrics/non-rigid_distances.txt");
    ofstream sumfile("data/metrics/non-rigid_summary.txt");

    outfile << "SourceID\tTargetID\tR3 Error" << endl;
    outfile << "-------------------------------------" << endl;
    for (int i = 0; i < size; i++) {
        int s_idx = nrr.source[i];
        int t_idx = nrr.target[i];

        double d = source_points[s_idx].distanceTo(target_points[s_idx]);
        if (d > max_distance) {
            max_distance = d;
        }
        total_distance += d;

        outfile << s_idx << " " << t_idx << " " << d << endl;
    }
    sumfile << "Summary" << endl;
    sumfile << "-------------------------------------" << endl;
    sumfile << "Total error: " << total_distance << endl;
    sumfile << "Average error: " << total_distance / size << endl;
    sumfile << "Max error: " << max_distance << endl;
}


int main(int argc, char ** argv) {
    // Metric points
    map<string, int> s_metrics = get_points("data/metrics/source.txt");
    map<string, int> t_metrics = get_points("data/metrics/target.txt");

    // read the map
    M m = readMap("data/registration/map.txt");
    
    // Read the source and target point clouds.
    vector<Point> sourcePoints = readPointCloud(argv[1]);
    vector<Point> targetPoints = readPointCloud(argv[2]);

    calculate_non_rigid_error(m, sourcePoints, targetPoints);

}