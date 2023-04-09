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
    // string f(fname);
    map<string, int> kp;
    string name;
    int vert_id;
    string line;
    std::ifstream infile(fname);
    while (std::getline(infile, line)) {
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
        double real;
        double imag;
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
        if (line.substr(0, 3) == "vt") {
            textures.push_back(line);
        }
        else if (line.substr(0, 2) == "f ") {
            faces.push_back(line);
        }
    }
}

std::string replace_substr(const std::string& str, const std::string& old_substr, const std::string& new_substr) {
    std::string result = str;
    size_t pos = result.find(old_substr);
    if (pos != std::string::npos) {
        result.replace(pos, old_substr.length(), new_substr);
    }
    return result;
}

string change_fpath(string fname) {
    cout << fname << endl;
    string nname = replace_substr(fname, "mapped", "transformed");
    cout << nname << endl;
    return nname;
}

void write_vertices(string fname) {
    string nname = change_fpath(fname);

    ofstream outfile(nname);
    for (int i = 0; i < vertices.size(); i++) {
        Complex v = vertices[i];
        outfile << "v " << v.real() << " " <<  v.imag() << " " << "0.0";
        vector<double> c = colors[i];
        // c[0] = r, c[1] = g, c[2] = b
        outfile << " " << c[0] << " " << c[1] << " " << c[2] << endl;
    }
    for (int i = 0; i < textures.size(); i++) {
        outfile << textures[i] << endl;
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
    
    // 1. Convert the uv coordinates of the Vertex to a complex type.
    Complex z1 = vertices[nosetip_id];
    Complex z2 = vertices[left_eye_id];
    Complex z3 = vertices[right_eye_id];

    Complex mb_nt{0.0, 0.0}; // w0
    Complex mb_le = (z2 - z1) / (1.0 - conj(z1) * z2);
    Complex mb_re = (z3 - z1) / (1.0 - conj(z1) * z3);

    double theta = atan(imag(mb_re - mb_le)/real(mb_le - mb_re));

    for (int i = 0; i < vertices.size(); i++) {
        Complex z = vertices[i];
        cout << z.imag() << " " << z.real() << endl;
        Complex w = mobius_transform(z, z1, theta);
        cout << w.imag() << " " << w.real() << endl;
        vertices[i] = w;

    }

}


int main(int argc, char * argv[]){
    map<string, int> keypoints = get_keypoints(argv[2]);

    read_vertices(argv[1]);
    cout << "Faces length: " << faces.size() << endl;
    cout << "Vertices Length " << vertices.size() << endl;

    Complex nt = vertices[keypoints["nosetip"]];
    Complex le = vertices[keypoints["left_eye"]];
    Complex re = vertices[keypoints["right_eye"]];

    cout << "Nosetip vertex " << nt << endl;
    cout << "Left eye vertex " << le << endl;
    cout << "Right eye vertex " << re << endl;

    compute_mobius_transform(keypoints["nosetip"], keypoints["left_eye"], keypoints["right_eye"]);

    string fpath_transformed = change_fpath(argv[1]);

    write_vertices(fpath_transformed);
    
}