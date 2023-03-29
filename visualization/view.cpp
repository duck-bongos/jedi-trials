/*!CHarmonicMapMesh g_mesh;
CHarmonicMap g_mapper;


 draw g_mesh
void drawUv()
{
    glEnable(GL_LIGHTING);

    glLineWidth(1.0);
    glColor3f(229.0 / 255.0, 162.0 / 255.0, 141.0 / 255.0);
    for (CHarmonicMapMesh::MeshFaceIterator fiter(&g_mesh); !fiter.end(); ++fiter)
    {
        glBegin(GL_POLYGON);
        CHarmonicMapFace *pF = *fiter;
        for (CHarmonicMapMesh::FaceVertexIterator fviter(pF); !fviter.end(); ++fviter)
        {
            CHarmonicMapVertex *pV = *fviter;
            CPoint2 &uv = pV->uv();
            CPoint &rgb = pV->rgb();
            CPoint n;
            switch (g_shade_flag)
            {
            case 0:
                n = pF->normal();
                break;
            case 1:
                n = pV->normal();
                break;
            }
            glNormal3d(n[0], n[1], n[2]);
            glColor3f(rgb[0], rgb[1], rgb[2]);
            glVertex3d(uv[0], uv[1], 0);
        }
        glEnd();
    }
}
*/