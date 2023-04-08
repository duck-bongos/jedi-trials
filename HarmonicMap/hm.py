"""Rewrite the harmonic mapped coordinates.

Rewrite such that there vertex RGB values
are matched with the texture coordinates.
Then remove the vertex values.

"""

from pathlib import Path
import sys
from typing import List

import numpy as np


def read_obj(fpath: Path):
    with open(fpath) as f:
        lines = f.readlines()
        vt = [line for line in lines if line.startswith("vt ")]
        vs = [line for line in lines if line.startswith("v ")]
        fs = [line for line in lines if line.startswith("f ")]

    vt = [line[3:].strip().split(" ") for line in vt]
    vt = [[float(x) for x in line] for line in vt]

    vs = [line[2:].strip().split(" ") for line in vs]
    vs = [[float(x) for x in line] for line in vs]

    vs = np.array(vs)
    vt = np.array(vt)
    return vs, vt, fs


def combine(vertices: np.ndarray, textures: np.ndarray):
    h = np.hstack([textures[:, :2], np.zeros((vertices.shape[0], 1)), vertices[:, 3:]])
    return h


def write_out(fpath: Path, full: np.ndarray, textures: np.ndarray, faces: List[str]):
    with open(fpath, "w") as fp:
        for i in range(full.shape[0]):
            fp.write(f"v {' '.join([str(x) for x in full[i,:]])}\n")
        for i in range(textures.shape[0]):
            fp.write(f"vt {' '.join([str(x) for x in textures[i,:]])}\n")
        for i in range(len(faces)):
            fp.write(f"{faces[i]}")


if __name__ in "__main__":
    # read in collapsed
    # c_vertices, c_textures, _ = read_obj(sys.argv[1])
    h_vertices, h_textures, h_faces = read_obj(sys.argv[1])
    hstack = combine(h_vertices, h_textures)

    write_out(sys.argv[1], hstack, h_textures, h_faces)
    print()
