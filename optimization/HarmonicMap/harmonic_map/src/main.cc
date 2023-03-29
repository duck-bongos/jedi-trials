/*!
 * author: Dan Billmann
 * coauthor: David Xianfeng Gu (lines 24 - 91)
 * date: March 27, 2023
 *
 */
#include <cstring>
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

const char *append_name(const char *fpath_name)
{
    const char *dot_pos = strrchr(fpath_name, '.');
    if (dot_pos != nullptr)
    {
        size_t len_prefix = dot_pos - fpath_name;
        size_t len_suffix = strlen(dot_pos);
        size_t len_new = len_prefix + strlen("_uv_coordinates.") + len_suffix + 1;
        char *new_fpath_name = new char[len_new];
        strncpy_s(new_fpath_name, len_new, fpath_name, len_prefix);
        new_fpath_name[len_prefix] = '\0';
        strcat_s(new_fpath_name, len_new, "_uv_coordinates");
        strcat_s(new_fpath_name, len_new, dot_pos);
        return new_fpath_name;
    }
    else
    {
        return fpath_name;
    }
}

void write_uv(CHarmonicMapMesh pMesh, const char *output)
{
    std::fstream zzz(output, std::fstream::out);
    if (zzz.fail())
    {
        fprintf(stderr, "Error in opening file %s\n", output);
        return;
    }
    int vid = 1;

    std::list<CHarmonicMapVertex *> m_verts = pMesh.vertices();
    for (typename std::list<CHarmonicMapVertex *>::iterator viter = m_verts.begin(); viter != m_verts.end(); viter++)
    {
        CHarmonicMapVertex *v = *viter;
        v->id() = vid++;
    }

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
    printf("Computing iterative map...\n");
    // g_mapper.iterative_map(0.005);
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
    printf("Attempting to write UV coordinates to file...");
    const char *uv_name = append_name(argv[2]);
    write_uv(g_mesh, uv_name);
    printf("Wrote UV coordinates to file...");
    delete[] uv_name;

    return EXIT_SUCCESS;
}