#include <math.h>
#include <iostream>
#include <stdio.h>
#include <stdlib.h>

#include "HarmonicMap.h"
#include "HarmonicMapMesh.h"

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

#include <cstring>

const char *get_new_pathname(const char *string)
/*!
Convert the input path name to the output pathname

input: data/source/
*/
{
    const char *tail = strrchr(string, '/') + 1;
    const char *new_string = nullptr;
    if (strstr(string, "source") != nullptr)
    {
        new_string = "data/optimized/source/";
    }
    else if (strstr(string, "target") != nullptr)
    {
        new_string = "data/optimized/target/";
    }

    if (new_string != nullptr)
    {
        size_t len = strlen(tail) + strlen(new_string) + 1;
        char *result = new char[len]; // make sure to delete[]
        strcpy(result, new_string);
        strcat(result, tail);
        return result;
    }
    else
    {
        return string;
    }
}

int main(int argc, char *argv[])
/*! Run this as

<executable> <input_object.obj> <output_object.obj>
*
*/

{
    const char *new_pathname;
    std::string mesh_name;

    if (argc < 2)
    {
        printf("Usage:\n%s input.m\n--or--\n%s input.obj\n", argv[0], argv[0]);
        return EXIT_FAILURE;
    }
    else if (argc == 2)
    {
        std::string mesh_name(argv[1]);
        /*!
         * Get the new pathname
         */
        const char *new_pathname = get_new_pathname(argv[1]);
    }
    else
    {
        // Read in the mesh from the file
        std::string mesh_name(argv[1]);

        /*!
         * Get the new pathname
         */
        printf("Using provided path, %s, as the output file path.\n", argv[2]);
        const char *new_pathname = argv[2];
    }

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
        printf("FUCK!?? %s was provided ", mesh_name.c_str());
        return EXIT_FAILURE;
    }

    // prepare the mesh for computation
    normalizeMesh(&g_mesh);
    computeNormal(&g_mesh);
    g_mapper.set_mesh(&g_mesh);

    /*!
    Compute the Harmonic Map
    */
    g_mapper.map();

    /*!
     * Write the computed results to a file
     * */
    g_mesh.write_obj(new_pathname);
    printf("\nWrote to %s.\n", new_pathname);

    /*!free the memory*/
    delete[] new_pathname;
    return EXIT_SUCCESS;
}