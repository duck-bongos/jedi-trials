#include <iostream>
#include <stdio.h>
#include <stdlib.h>

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


unordered_map* read_keypoints(char* fname_keypoints) {
    
}


int main(int argc, char* argv[]) {

    if (argc < 3) {
        printf("You need 3 arguments you silly goose!\n");
        printf("Example Usage: ./mobius <data/mapped/source.obj> <data/keypoints/source.txt>\n");
        return -1;
    }

    int id_nt = 13257; // nosetip vertex ID, hard-coded
    int id_le = 7517;  // left eye vertex ID, hard-coded
    int id_re = 7769;  // right eye vertex ID, hard-coded



    printf("Computing Möbius Transformation...\n");
    compute_uv_mobius_transform(&g_mesh, id_nt, id_le, id_re);
    printf("Computed Möbius Transformation.\n");

    printf("Attempting to write texture coordinates to file...\n");
    write_uv(g_mesh, "../../data/mobius_mapped_target.obj");
    printf("Wrote texture coordinates to file...\n");
}    