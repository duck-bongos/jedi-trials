#include<math.h>
#include<iostream>
#include<stdio.h>
#include<stdlib.h>

#include "HarmonicMap.h"
#include "HarmonicMapMesh.h"

using namespace MeshLib;

// GLOBALS
CHarmonicMapMesh g_mesh;
CHarmonicMap g_mapper;



int main(int argc, char * argv[]) {
	if (argc < 2)
	{
		printf("Usage:\n%s input.m\n--or--\n%s input.obj", argv[0], argv[0]);
		return EXIT_FAILURE;
	}

	// Read in the mesh from the file
	std::string mesh_name(argv[1]);

	if (strutil::endswith(mesh_name, ".m"))
	{
		g_mesh.read_m(mesh_name.c_str());
	}
	else if (strutil::endswith(mesh_name, ".obj")) 
	{
		g_mesh.read_obj(mesh_name.c_str());
	}
	else
	{
		printf("Only file extensions '.m' and '.obj' supported.\n");
		return EXIT_FAILURE;
	}

	// prepare the mesh for computation
	normalizeMesh(&g_mesh);
    computeNormal(&g_mesh);
    g_mapper.set_mesh(&g_mesh);
    
    /*Compute the Harmonic Map*/
    g_mapper.iterative_map();

    /*!
     * Write the computed results to a file
     * */
    g_mesh.write_obj("/Users/dan/Desktop/flat_dan.obj");
    return EXIT_SUCCESS;

}