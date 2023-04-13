#include <complex.h>
#include <math.h>
#include <string>
#include <iostream>
#include <fstream>
#include <map>
#include <vector>
#include <tuple>

using namespace std;

typedef complex<double> Complex;
typedef vector<double> color;

vector<Complex> vertices;
vector<vector<double> > colors;
vector<string> textures;
vector<string> faces;

map<string, int> get_keypoints(string fname) {
    map<string, int> kp;
    string name;
    int vert_id;
    string line;
    ifstream infile(fname);
    while (getline(infile, line)) {
        istringstream iss(line);
        if (!(iss >> name >> vert_id)) { break;}
        kp[name] = vert_id;
    }

    return kp;
}

void read_vertices(string fname) {
    string line;
    ifstream infile(fname);
    while (getline(infile, line)) {
        istringstream iss(line);
        string v;
        vector<double> c;
        double x, y, skip, r, g, b;
        if (line.substr(0, 2) == "v ") {
            iss >> v >> x >> y >> skip >> r >> g >> b;
            c.push_back(r);
            c.push_back(g);
            c.push_back(b);
            colors.push_back(c);
            Complex z(x, y);
            vertices.push_back(z);
        }
        if (line.substr(0, 3) == "vt ") {
            textures.push_back(line);
        }
        else if (line.substr(0, 2) == "f ") {
            faces.push_back(line);
        }
    }
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
    string nname = replace_substr(fname, "mapped", "transformed");
    return nname;
}

void write_vertices(string fname) {
    string nname = change_fpath(fname);

    ofstream outfile(nname);
    for (int i = 0; i < vertices.size(); i++) {
        Complex v = vertices[i];
        outfile << "v " << v.real() << " " <<  v.imag() << " 0.0";
        vector<double> c = colors[i];
        // c[0] = r, c[1] = g, c[2] = b
        outfile << " " << c[0] << " " << c[1] << " " << c[2] << endl;
    }
    cout << "textures size " << textures.size() << endl;
    for (int i = 0; i < textures.size(); i++) {
        string t = textures[i];
        outfile << t << endl;
    }

    for (int i = 0; i < faces.size(); i++) {
        outfile << faces[i] << endl;
    }
}

Complex mobius_transform(Complex z, Complex origin, double theta) {
    Complex i(0, 1);
    Complex z_ = exp(i*theta) * ((z - origin)/(1.0 - (conj(origin) * z)));
    return z_;
}

void compute_mobius_transform(int nosetip_id, int left_eye_id, int right_eye_id) {
    printf("Setting constants for Möbius transform...\n");
    
    Complex z1 = vertices[nosetip_id];
    Complex z2 = vertices[left_eye_id];
    Complex z3 = vertices[right_eye_id];

    Complex mb_le = (z2 - z1) / (1.0 - conj(z1) * z2);
    Complex mb_re = (z3 - z1) / (1.0 - conj(z1) * z3);

    double theta = atan(imag(mb_re - mb_le)/real(mb_le - mb_re));

    for (int i = 0; i < vertices.size(); i++) {
        Complex z = vertices[i];
        Complex w = mobius_transform(z, z1, theta);
        vertices[i] = w;
    }
}

int main(int argc, char * argv[]){
    map<string, int> keypoints = get_keypoints(argv[2]);

    read_vertices(argv[1]);

    cout << textures.size() << endl;
    cout << textures[0] << endl;

    Complex nt = vertices[keypoints["nosetip"]];
    Complex le = vertices[keypoints["left_eye"]];
    Complex re = vertices[keypoints["right_eye"]];

    cout << "Computing Möbius transformation." << endl;

    compute_mobius_transform(keypoints["nosetip"], keypoints["left_eye"], keypoints["right_eye"]);

    string fpath_transformed = change_fpath(argv[1]);

    write_vertices(fpath_transformed);

    cout << "Computed Möbius transformation." << endl;
    cout << "Wrote results to " << fpath_transformed << endl;
    
}