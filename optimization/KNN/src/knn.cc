#include <fstream>
#include <regex>
#include <string>
#include <vector>
#include <iostream>
#include <unordered_map>
#include <eigen3/Eigen/Dense>

using namespace std;
using namespace Eigen;

typedef Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> MatrixXdRM;

Eigen::MatrixXd convert(const std::string& fpath) {
    // vertex pattern
    std::ifstream file(fpath);
    std::string str((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
    std::regex re("vt\\ .*");
    std::vector<std::vector<double> > result;
    std::sregex_iterator it(str.begin(), str.end(), re);
    std::sregex_iterator end;
    while (it != end) {
        std::string match_str = it->str();
        std::vector<double> match_vec;
        std::string::size_type pos = match_str.find(' ');
        match_vec.push_back(std::stod(match_str.substr(pos + 1)));
        pos = match_str.find(' ', pos + 1);
        match_vec.push_back(std::stod(match_str.substr(pos + 1)));
        result.push_back(match_vec);
        ++it;
    }
    // Allocate matrix and copy data
    Eigen::MatrixXd matrix(result.size(), 2);
    for (int i = 0; i < result.size(); i++) {
        matrix(i, 0) = result[i][0];
        matrix(i, 1) = result[i][1];
    }
    return matrix;
}


unordered_map<int, int> knn(MatrixXd source, MatrixXd target) {
    unordered_map<int, int> mmm;
    for (int i = 0; i < source.rows(); i++) {
        double min_dist = numeric_limits<double>::infinity();
        int min_dist_id = 0;
        for (int j = 0; j < target.rows(); j++) {
            double d = (source.row(i) - target.row(j)).norm();
            if (d < min_dist) {
                min_dist = d;
                min_dist_id = j;
            }
        }
        mmm[i] = min_dist_id;
        if (i % 1000 == 0){
            std::cout << "Completed " << i << "th iteration." << std::endl;
        }
    }
    return mmm;
}


std::unordered_map<int, int> v_knn(const MatrixXdRM& source, const MatrixXdRM& target) {
    int n = source.rows();
    int m = target.rows();
    Eigen::VectorXd distances(n);
    std::unordered_map<int, int> mmm;
    for (int i = 0; i < n; i++) {
        Eigen::VectorXd a = source.row(i);
        distances = (target.rowwise() - a.transpose()).rowwise().norm();
        int min_dist_id;
        double min_dist = distances.minCoeff(&min_dist_id);
        mmm[i] = min_dist_id;
    }
    return mmm;
}


void write_map_to_file(const std::unordered_map<int, int>& my_map, const std::string& filename) {
    std::ofstream file(filename);
    if (file.is_open()) {
        for (const auto& [key, value] : my_map) {
            file << key << "->" << value << std::endl;
        }
        file.close();
    } else {
        std::cerr << "Error opening file: " << filename << std::endl;
    }
}


int main(int argc, char * argv[]) {
    MatrixXd source = convert(argv[1]);
    MatrixXd target = convert(argv[2]);
    // fill source and target arrays

    auto result = v_knn(source, target);
    
    // process result
    write_map_to_file(result, argv[3]);

    return 0;
}
