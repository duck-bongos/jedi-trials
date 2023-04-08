/*!
 * author: Dan Billmann
 * advisor: David Xianfeng Gu
 * date: March 27, 2023
 *
 */
#include <complex>
#include <cstring>
#include <string.h>
#include <math.h>
#include <iostream>
#include <stdio.h>
#include <stdlib.h>

#include "HarmonicMap.h"
#include "HarmonicMapMesh.h"
// #include <yaml-cpp/yaml.h>

typedef std::complex<double> Complex;

using namespace MeshLib;

// GLOBALS
CHarmonicMapMesh g_mesh;
CHarmonicMap g_mapper;

/*! Normalize g_mesh
 * \param pMesh the input g_mesh
 */
void normalizeMesh(CHarmonicMapMesh *pMesh)
{
    CPoint s(0, 0, 0);
    for (CHarmonicMapMesh::MeshVertexIterator viter(pMesh); !viter.end(); ++viter)
    {
        CHarmonicMapVertex *v = *viter;
        s = s + v->point();
    }
    s = s / pMesh->numVertices();

    for (CHarmonicMapMesh::MeshVertexIterator viter(pMesh); !viter.end(); ++viter)
    {
        CHarmonicMapVertex *v = *viter;
        CPoint p = v->point();
        p = p - s;
        v->point() = p;
    }

    double d = 0;
    for (CHarmonicMapMesh::MeshVertexIterator viter(pMesh); !viter.end(); ++viter)
    {
        CHarmonicMapVertex *v = *viter;
        CPoint p = v->point();
        for (int k = 0; k < 3; k++)
        {
            d = (d > fabs(p[k])) ? d : fabs(p[k]);
        }
    }

    for (CHarmonicMapMesh::MeshVertexIterator viter(pMesh); !viter.end(); ++viter)
    {
        CHarmonicMapVertex *v = *viter;
        CPoint p = v->point();
        p = p / d;
        v->point() = p;
    }
};

/*! Compute the face normal and vertex normal
 * \param pMesh the input g_mesh
 */
void computeNormal(CHarmonicMapMesh *pMesh)
{
    for (CHarmonicMapMesh::MeshVertexIterator viter(pMesh); !viter.end(); ++viter)
    {
        CHarmonicMapVertex *v = *viter;
        CPoint n(0, 0, 0);
        for (CHarmonicMapMesh::VertexFaceIterator vfiter(v); !vfiter.end(); ++vfiter)
        {
            CHarmonicMapFace *pF = *vfiter;

            CPoint p[3];
            CHalfEdge *he = pF->halfedge();
            for (int k = 0; k < 3; k++)
            {
                p[k] = he->target()->point();
                he = he->he_next();
            }

            CPoint fn = (p[1] - p[0]) ^ (p[2] - p[0]);
            pF->normal() = fn / fn.norm();
            n += fn;
        }

        n = n / n.norm();
        v->normal() = n;
    }
};

Complex* calculate_mobius_coefficients(Complex z1, Complex z2, Complex z3, Complex w1, Complex w2, Complex w3) {
    /*!
    Take in the two sets of 3 points () and () and return the imaginary coefficients
    (a, b, c, d) for the function 

    Array indices are returned in alphabetical order s.t. imag_coeff[0] = a, imag_coeff[3] = d;
    */
    Complex* imag_coeff = new Complex[4];

    // Algebraic solutions of the imaginary coefficients
    
    // a
    imag_coeff[0] = (w1 * (z2 - z3) + w2 * (z3 - z1) + w3 * (z1 - z2)) / ((z1 - z2) * (z3 - z1));
    
    // b
    imag_coeff[1] = (w1*z2* (z3 - z1) + w2 * z3 *(z1-z2) + w3*z1*(z2-z3)) / ((z1-z2)*(z3-z1));
    
    // c
    imag_coeff[2] = (w1*(z2*z3-z3*z1) + w2*(z3*z1-z1*z2) + w3*(z1*z2-z2*z3)) / ((z1-z2)*(z3-z1));
    
    // d
    imag_coeff[3] = (w1*z2*z3*(z2-z3) + w2*z3*z1*(z3-z1) + w3*z1*z2*(z1-z2)) / ((z1-z2)*(z3-z1));

    return imag_coeff; 
}

Complex mobius_transform(Complex z, Complex origin, double theta) {
    Complex i(0, 1);
    Complex z_ = std::exp(i*theta) * ((z - origin)/(1.0 - (std::conj(origin) * z)));
    return z_;
}

void compute_uv_mobius_transform(CHarmonicMapMesh *pmesh, int nosetip_id, int left_eye_id, int right_eye_id) {
    /*!
    Compute the Möbius transform using the nosetip (1), left eye corner (2), and 
    right eye corner (3) as the fixed points on a 2D disc.

    Abbreviations: 
    ---------------
    nosetip -> "nt"
    left eye corner -> "le"
    right eye corner -> "re"
    Möbius -> "mb"

    map (z1, z2, z3) |-> (w1, w2, w3) s.t :
     - w1 = 0+0i, 
     - w2 = -.2+.2i
     - w3 = .2+.2i
    
    0. Acccess the vertices to find the vertices at the input IDs.
    1. Convert the uv coordinates of the Vertex to a complex type
        e.g uv[0] = 0, uv[1] = 1
        complex_uv = 0+1i
    2. Fix the new point locations
    3. Build the Möbius transform
    4. Iterate through every Vertex
    5. Convert the point to a complex value
    6. Compute the Möbius values.
    7. Convert the computed w from the complex plane to the coordinate plane
    8. Assign the computed point to the vertex
    */
    printf("Setting constants for Möbius transform...\n");
    // 0. Acccess the vertices to find the vertices at the input IDs.
    CPoint2 uv_nt = pmesh->idVertex(nosetip_id)->uv();
    CPoint2 uv_le = pmesh->idVertex(left_eye_id)->uv();
    CPoint2 uv_re = pmesh->idVertex(right_eye_id)->uv();

    // 1. Convert the uv coordinates of the Vertex to a complex type.
    Complex i_nt{uv_nt[0], uv_nt[1]};  // z1
    Complex i_le{uv_le[0], uv_le[1]};  // z2
    Complex i_re{uv_re[0], uv_re[1]};  // z3
    
    // 2. Fix the new point locations
    Complex mb_nt{0.0, 0.0};  // w1
    // Complex mb_le{-0.2, 0.2};  // w2 
    // Complex mb_re{0.2, 0.2};  // w3

    // w1 = (z2-z1)  (1-conj(z1)*z2)
    Complex mb_le = (i_le - i_nt) / (1.0 - std::conj(i_nt)*i_le);
    // w2 = (z3 - z1) / (1-conj(z1)*z3)
    Complex mb_re = (i_re - i_nt) / (1.0 - std::conj(i_nt)*i_re);
    double theta = atan(std::imag(mb_re - mb_le)/std::real(mb_le - mb_re));

    // construct equation
    
    // 3. build the Möbius transform equation (z1, z2, z3) |-> (w1, w2, w3)
    // printf("Calculating Möbius coefficients...\n");
    // Complex* coeff = calculate_mobius_coefficients(i_nt, i_le, i_re, mb_nt, mb_le, mb_re);
    // const Complex a = coeff[0];
    // const Complex b = coeff[1];
    // const Complex c = coeff[2];
    // const Complex d = coeff[3];
    // printf("Möbius coefficients set.\n");
    printf("Set constants for Möbius transform.\n");
    printf("Iterating through mesh, recomputing Texture coordinates...\n");
    // 4. Iterate through the Vertices
    for (CHarmonicMapMesh::MeshVertexIterator viter(pmesh); !viter.end(); ++viter)
    {
        CHarmonicMapVertex *vertex = *viter;

        // 5. Convert the point to a complex value
        Complex z{vertex->uv()[0], vertex->uv()[1]};

        /*! 6. Compute the Möbius values. 
            
            w = (az + b) / (cz + d)

            Author's note: I abhor single-character variables, 
            but I will make an exception to keep in line with 
            the mathematical notation.

        */ 
        Complex w = mobius_transform(z, i_nt, theta);
        std::cout << "------------------------\n" << "W: " << w.real() << " " << w.imag() << "\nZ: " << z.real() << " " << z.imag() << "\n" << std::endl;
        // 7. Convert the computed w from the complex plane to the coordinate plane
        CPoint2 coord_point;
        coord_point[0] = w.real();
        coord_point[1] = w.imag();

        // 8. Assign the computed point to the vertex
        vertex->uv() = coord_point;
    }
    printf("Texture coordinate reassignment complete.\n");

    return;
}


void write_uv(CHarmonicMapMesh pMesh, std::string output)
{
    const char* ooo = output.c_str();
    std::ofstream zzz(output);
    if (zzz.fail())
    {
        printf("Error in opening file %s\n", ooo);
        return;
    }
    int vid = 1;

    std::list<CHarmonicMapVertex *> m_verts = pMesh.vertices();
    // for (typename std::list<CHarmonicMapVertex *>::iterator viter = m_verts.begin(); viter != m_verts.end(); viter++)
    // {
    //     CHarmonicMapVertex *v = *viter;
    //     v->id() = vid++;
    // }

    // vertices
    for (typename std::list<CHarmonicMapVertex *>::iterator viter = m_verts.begin(); viter != m_verts.end(); viter++)
    {
        CHarmonicMapVertex *v = *viter;
        CPoint2 &uv = v->uv();
        CPoint &rgb = v->rgb();

        zzz << "v";
        for (int i = 0; i < 2; i++)
        {
            zzz << " " << uv[i];
        }
        // third vertex = 0
        zzz << " 0";

        // add RGB values
        for (int i = 0; i < 3; i++)
        {
            zzz << " " << rgb[i];
        }
        zzz << std::endl;
    }

    // textures
    for (typename std::list<CHarmonicMapVertex *>::iterator viter = m_verts.begin(); viter != m_verts.end(); viter++)
    {
        CHarmonicMapVertex *v = *viter;
        CPoint2 uv = v->uv();

        zzz << "vt";

        for (int i = 0; i < 2; i++)
        {
            zzz << " " << uv[i];
        }

        zzz << std::endl;
    }

    // faces
    for (CHarmonicMapMesh::MeshFaceIterator fiter(&g_mesh); !fiter.end(); ++fiter)
    {
        CHarmonicMapFace *pF = *fiter;
        // same as faceHalfedge(f)
        CHarmonicMapHalfEdge *he = (CHarmonicMapHalfEdge *)pF->halfedge();

        zzz << "f";

        do
        {
            int vid = he->target()->id();
            zzz << " " << vid << "/" << vid << "/" << vid;
            // same as halfedgeNext(he);
            he = (CHarmonicMapHalfEdge *)he->he_next();

        } while (he != pF->halfedge());
        zzz << std::endl;
    }
    zzz.close();
}


char* get_fname(char* fname){
    /*source.txt and target.txt have same # of characters*/
    int n = 10;
    int len = std::strlen(fname);

    if (n > len) {
        n = len;
    }
    char* last_n = fname + len - n;
    return last_n;
}


int main(int argc, char *argv[])
/*! Run this as

<executable> <input_object.obj> <output_object.obj>
*
*/

{
    if (argc < 3)
    {
        printf("Usage:\n%s <input.m> <output.m>\n--or--\n%s <input.obj> <output.obj>\n", argv[0], argv[0]);
        return EXIT_FAILURE;
    }

    std::string mesh_name(argv[1]);

    if (strutil::endsWith(mesh_name, ".m"))
    {
        g_mesh.read_m(mesh_name.c_str());
    }
    else if (strutil::endsWith(mesh_name, ".obj"))
    {
        g_mesh.read_obj(mesh_name.c_str());
    }
    else
    {
        printf("Only file extensions '.m' and '.obj' supported.\n");
        return EXIT_FAILURE;
    }

    // prepare the mesh for computation
    printf("Normalizing mesh...\n");
    normalizeMesh(&g_mesh);
    printf("Mesh normalized.\n");

    printf("Computing normals...\n");
    computeNormal(&g_mesh);
    printf("Normals computed.\n");

    printf("Setting mesh...\n");
    g_mapper.set_mesh(&g_mesh);
    printf("Mesh set.\n");

    /*!
    Compute the Harmonic Map
    */
    printf("Computing harmonic map...\n");
    g_mapper.map();
    printf("Computation complete.\n");

    /*!
     * Write the computed results to a file
     * */
    if (strutil::endsWith(argv[2], ".m"))
    {
        g_mesh.write_m(argv[2]);
    }
    else if (strutil::endsWith(argv[2], ".obj"))
    {
        g_mesh.write_obj(argv[2]);
    }
    else
    {
        printf("Only file extensions '.m' and '.obj' supported.\n");
        return EXIT_FAILURE;
    }
    printf("\nWrote to %s.\n", argv[2]);

    /*!
    Write uv coordinates out as .obj file
    */
    // printf("Attempting to write texture coordinates to file...\n");
    // char *fname = get_fname(argv[2]);
    // // std::string fname_ = std::string(fname);
    // // std::string dir = std::string("../data/mapped");
    // // std::string fname_mapped = dir + fname;
    // // write_uv(g_mesh, fname_mapped.c_str());
    // std::string fn = std::string("../data/mapped") + std::string(fname);
    // g_mesh.write_obj(fn.c_str());
    // printf("Wrote texture coordinates to file...\n");
    // delete[] fname;

    return EXIT_SUCCESS;
}