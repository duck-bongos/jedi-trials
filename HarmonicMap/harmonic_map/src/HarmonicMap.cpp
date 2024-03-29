#include <math.h>
#include <float.h>

#include <Eigen/Sparse>

#include "HarmonicMap.h"

#ifndef M_PI
#define M_PI 3.141592653589793238462643383279
#endif

void MeshLib::CHarmonicMap::set_mesh(CHarmonicMapMesh *pMesh)
{
    m_pMesh = pMesh;

    // 1. compute the weights of edges
    printf("Calculating edge weight...\n");
    _calculate_edge_weight();
    printf("Calculated edge weight.\n");

    // 2. map the boundary to unit circle
    printf("Setting boundary...\n");
    _set_boundary();
    printf("Set boundary.\n");

    // 3. initialize the map of interior vertices to (0, 0)
    using M = CHarmonicMapMesh;
    for (M::MeshVertexIterator viter(m_pMesh); !viter.end(); ++viter)
    {
        M::CVertex *pV = *viter;
        if (pV->boundary())
            continue;

        pV->uv() = CPoint2(0, 0);
    }
}

double MeshLib::CHarmonicMap::step_one()
{
    if (!m_pMesh)
    {
        std::cerr << "Should set mesh first!" << std::endl;
        return DBL_MAX;
    }

    using M = CHarmonicMapMesh;

    // move each interior vertex to its weighted center of neighbors
    double max_error = -DBL_MAX;
    for (M::MeshVertexIterator viter(m_pMesh); !viter.end(); ++viter)
    {
        M::CVertex *pV = *viter;
        if (pV->boundary())
            continue;

        double sw = 0;
        CPoint2 suv(0, 0);
        for (M::VertexVertexIterator vviter(pV); !vviter.end(); vviter++)
        {
            M::CVertex *pW = *vviter;
            M::CEdge *pE = m_pMesh->vertexEdge(pV, pW);
            double w = pE->weight();
            sw += w;
            suv = suv + pW->uv() * w;
        }
        suv /= sw;

        double error = (pV->uv() - suv).norm();
        max_error = (error > max_error) ? error : max_error;

        pV->uv() = suv;
    }

    printf("Current max error is %g\n", max_error);
    return max_error;
}

void MeshLib::CHarmonicMap::iterative_map(double epsilon)
{
    if (!m_pMesh)
    {
        std::cerr << "Should set mesh first!" << std::endl;
        return;
    }

    using M = CHarmonicMapMesh;

    int count = 0;

    // take steps until it converges.
    while (true)
    {
        double error = this->step_one();
        if (error < epsilon)
            break;
        count += 1;

        printf("Completed %s iterations.\n", std::to_string(count).c_str());
    }
}
void MeshLib::CHarmonicMap::map()
{
    if (!m_pMesh)
    {
        std::cerr << "Should set mesh first!" << std::endl;
        return;
    }

    using M = CHarmonicMapMesh;

    // 1. Initialize
    int vid = 0; // interior vertex id
    int bid = 0; // boundary vertex id
    for (M::MeshVertexIterator viter(m_pMesh); !viter.end(); ++viter)
    {
        M::CVertex *pV = *viter;

        if (pV->boundary())
            pV->idx() = bid++;
        else
            pV->idx() = vid++;
    }

    int interior_vertices = vid;
    int boundary_vertices = bid;

    // 2. Set the matrix A and B
    std::vector<Eigen::Triplet<double>> A_coefficients;
    std::vector<Eigen::Triplet<double>> B_coefficients;

    for (M::MeshVertexIterator viter(m_pMesh); !viter.end(); ++viter)
    {
        M::CVertex *pV = *viter;
        if (pV->boundary())
            continue;
        int vid = pV->idx();

        double sw = 0;
        for (M::VertexVertexIterator witer(pV); !witer.end(); ++witer)
        {
            M::CVertex *pW = *witer;
            int wid = pW->idx();

            M::CEdge *e = m_pMesh->vertexEdge(pV, pW);
            double w = e->weight();

            if (pW->boundary())
            {
                B_coefficients.push_back(Eigen::Triplet<double>(vid, wid, w));
            }
            else
            {
                A_coefficients.push_back(Eigen::Triplet<double>(vid, wid, -w));
            }
            sw += w;
        }
        A_coefficients.push_back(Eigen::Triplet<double>(vid, vid, sw));
    }

    Eigen::SparseMatrix<double> A(interior_vertices, interior_vertices);
    A.setZero();
    Eigen::SparseMatrix<double> B(interior_vertices, boundary_vertices);
    B.setZero();
    A.setFromTriplets(A_coefficients.begin(), A_coefficients.end());
    B.setFromTriplets(B_coefficients.begin(), B_coefficients.end());

    // 3. Solve the equations
    Eigen::ConjugateGradient<Eigen::SparseMatrix<double>> solver;
    std::cerr << "Eigen Decomposition" << std::endl;
    solver.compute(A);
    std::cerr << "Eigen Decomposition Finished" << std::endl;

    if (solver.info() != Eigen::Success)
    {
        std::cerr << "Waring: Eigen decomposition failed" << std::endl;
    }

    for (int k = 0; k < 2; k++)
    {
        Eigen::VectorXd b(boundary_vertices);
        // set boundary constraints vector b
        for (M::MeshVertexIterator viter(m_pMesh); !viter.end(); ++viter)
        {
            M::CVertex *pV = *viter;
            if (!pV->boundary())
                continue;
            int id = pV->idx();
            b(id) = pV->uv()[k];
        }

        Eigen::VectorXd c(interior_vertices);
        c = B * b;

        Eigen::VectorXd x = solver.solve(c); // Ax=c
        if (solver.info() != Eigen::Success)
        {
            std::cerr << "Waring: Eigen decomposition failed" << std::endl;
        }

        // set the images of the harmonic map to interior vertices
        for (M::MeshVertexIterator viter(m_pMesh); !viter.end(); ++viter)
        {
            M::CVertex *pV = *viter;
            if (pV->boundary())
                continue;
            int id = pV->idx();
            pV->uv()[k] = x(id);
        }
    }
}

void MeshLib::CHarmonicMap::_calculate_edge_weight()
{
    using M = CHarmonicMapMesh;

    // 1. compute edge length
    for (M::MeshEdgeIterator eiter(m_pMesh); !eiter.end(); ++eiter)
    {
        M::CEdge *pE = *eiter;
        M::CVertex *v1 = m_pMesh->edgeVertex1(pE);
        M::CVertex *v2 = m_pMesh->edgeVertex2(pE);
        pE->length() = (v1->point() - v2->point()).norm();
    }

    // 2. compute corner angle
    for (M::MeshFaceIterator fiter(m_pMesh); !fiter.end(); ++fiter)
    {
        M::CFace *pF = *fiter;
        M::CHalfEdge *pH[3];
        pH[0] = m_pMesh->faceHalfedge(pF);
        for (int i = 0; i < 3; i++)
        {
            pH[(i + 1) % 3] = m_pMesh->halfedgeNext(pH[i]);
        }

        double len[3];
        for (int i = 0; i < 3; i++)
        {
            len[i] = m_pMesh->halfedgeEdge(pH[i])->length();
        }

        for (int i = 0; i < 3; i++)
        {
            double a = len[(i + 1) % 3], b = len[(i + 2) % 3], c = len[i];
            pH[(i + 1) % 3]->angle() = _inverse_cosine_law(a, b, c);
        }
    }

    // 3. compute edge weight
    for (M::MeshEdgeIterator eiter(m_pMesh); !eiter.end(); ++eiter)
    {
        M::CEdge *pE = *eiter;

        if (!pE->boundary())
        {
            double theta[2];
            theta[0] = m_pMesh->halfedgeNext(m_pMesh->edgeHalfedge(pE, 0))->angle();
            theta[1] = m_pMesh->halfedgeNext(m_pMesh->edgeHalfedge(pE, 1))->angle();
            pE->weight() = std::cos(theta[0]) / std::sin(theta[0]) +
                           std::cos(theta[1]) / std::sin(theta[1]);
        }
        else
        {
            double theta = m_pMesh->halfedgeNext(m_pMesh->edgeHalfedge(pE, 0))->angle();
            pE->weight() = std::cos(theta) / std::sin(theta);
        }
    }
}

void MeshLib::CHarmonicMap::_set_boundary()
{
    using M = CHarmonicMapMesh;

    // 1. get the boundary half edge loop
    printf("Instantiating CBoundary boundary...\n");
    M::CBoundary boundary(m_pMesh);
    printf("Instantiated CBoundary boundary.\n");
    std::vector<M::CLoop *> &pLs = boundary.loops();
    if (pLs.size() != 1)
    {
        std::cerr << "Only topological disk accepted!" << std::endl;
        exit(EXIT_FAILURE);
    }
    M::CLoop *pL = pLs[0];
    std::list<M::CHalfEdge *> &pHs = pL->halfedges();

    // 2. compute the total length of the boundary
    printf("Computing total length of the boundary...\n");
    double sum = 0.0;
    std::list<M::CHalfEdge *>::iterator it;
    for (it = pHs.begin(); it != pHs.end(); ++it)
    {
        M::CHalfEdge *pH = *it;
        sum += m_pMesh->halfedgeEdge(pH)->length();
    }
    printf("Computed total length of the boundary.\n");

    // 3. parameterize the boundary using arc length parameter
    printf("Parameterizing the boundary using arc length parameter...\n");
    double len = 0.0;
    for (it = pHs.begin(); it != pHs.end(); ++it)
    {
        M::CHalfEdge *pH = *it;
        M::CVertex *pV = m_pMesh->halfedgeVertex(pH);

        len += m_pMesh->halfedgeEdge(pH)->length();
        double angle = len / sum * 2.0 * M_PI;
        pV->uv() = CPoint2(cos(angle), sin(angle));
    }
    printf("Parameterized the boundary using arc length parameter.\n");
}

double MeshLib::CHarmonicMap::_inverse_cosine_law(double a, double b, double c)
{
    double cs = (a * a + b * b - c * c) / (2.0 * a * b);
    assert(cs <= 1.0 && cs >= -1.0);
    return std::acos(cs);
}
