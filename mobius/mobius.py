from cmath import atan, exp, phase, pi, rect, sqrt
from pathlib import Path
import sys
from typing import List

import numpy as np


def read_keypoints(fpath: Path):
    keypoints = {}
    with open(fpath) as f:
        lines = f.readlines()
        lines = [line.strip().split(" ") for line in lines]

    keypoints = {k: int(v) for k, v in lines}
    return keypoints


def change_fname(fname: Path):
    name = fname.name
    data_dir = fname.parent.parent

    return data_dir / "transformed" / name


def read_obj(fname: Path):
    with open(fname) as f:
        fl = f.readlines()
    faces = [line for line in fl if line[0] == "f"]
    fl = [line.strip().split(" ") for line in fl if (line[0] == "v" or line[0] == "vt")]
    vertices = np.array([[float(x) for x in line[1:]] for line in fl if line[0] == "v"])
    textures = np.array(
        [[float(x) for x in line[1:]] for line in fl if line[0] == "vt"]
    )
    return vertices, textures, faces


def principal_arg(z):
    """
    Compute the principal argument of a complex number z.
    """
    if z.real > 0:
        # z lies in the right half-plane
        return phase(z)
    elif z.real < 0:
        # z lies in the left half-plane
        return phase(z) + pi
    else:
        # z lies on the imaginary axis
        if z.imag > 0:
            # z is on the positive imaginary axis
            return pi / 2
        elif z.imag < 0:
            # z is on the negative imaginary axis
            return -pi / 2
        else:
            # z is the origin, undefined
            return None


def deg(f: float):
    return (f * 180) / pi


def mobius(z: complex, origin: complex, theta: float):
    i = complex(0, 1)
    z_ = exp(i * theta) * ((z - origin) / (1.0 - (origin.conjugate() * z)))
    return z_


def run_mobius(
    z: complex,
    z1: complex,
    z2: complex,
    z3: complex,
    w1: complex,
    w2: complex,
    w3: complex,
):
    """
    (z, z1; z2, z3) = (w, w1; w2, w3)
    ((z - z2) * (z1 - z3)) / ((z - z3) * (z1 - z2)) = ((w - w2) * (w1 - w3)) / ((w - w3) * (w1 - w2))
    w = ((w2 * (w1 - w3) * (z - z3) * (z1 - z2) - w3 * (w1 - w2) * (z - z2) * (z1 - z3)) / ((z - z3) * (z1 - z2)))
    """
    num: complex = w2 * (w1 - w3) * (z - z3) * (z1 - z2) - w3 * (w1 - w2) * (z - z2) * (
        z1 - z3
    )
    den: complex = (z - z3) * (z1 - z2)
    w: complex
    if z == z3:
        w = w3
    elif z == z2:
        w = w2
    elif z == z1:
        w = w1
    else:
        w = num / den
    return w


def run_mobius_function(keypoints, textures, vertices):
    """
    CONSTANT MAPPING POINTS
    w1 = complex(-1, 1) / (2 * sqrt(2))
    w2 = complex(+1, 1) / (2 * sqrt(2))
    w3 = complex(0, 0)
    """
    z1 = complex(*tuple(textures[keypoints["left_eye"], :]))
    z2 = complex(*tuple(textures[keypoints["right_eye"], :]))
    z3 = complex(*tuple(textures[keypoints["nosetip"], :]))

    w1 = complex(-1, 1) / (2 * sqrt(2))
    w2 = complex(+1, 1) / (2 * sqrt(2))
    w3 = complex(0, 0)

    for i, t in enumerate(textures):
        z = complex(t[0], t[1])
        w = run_mobius(z, z1=z1, z2=z2, z3=z3, w1=w1, w2=w2, w3=w3)
        print(f"z: {z}\tw: {w}")
        textures[i][0] = w.real
        textures[i][1] = w.imag
        vertices[i][0] = w.real
        vertices[i][1] = w.imag
    return textures, vertices


def write_object(vertices: np.ndarray, textures: np.ndarray, faces: List[str]):
    with open("source.obj", "w") as s:
        for v in vertices:
            row = "v " + " ".join([str(x) for x in v]) + "\n"
            s.write(row)

        for vt in textures:
            row = "vt " + " ".join([str(x) for x in vt]) + "\n"
            s.write(row)

        for f in faces:
            s.write(f)


if __name__ in "__main__":
    if len(sys.argv) < 3:
        print("NO\n")
        sys.exit(1)

    vert, text, face = read_obj(sys.argv[1])
    keypoints = read_keypoints(sys.argv[2])

    text_, vert_ = run_mobius_function(keypoints, text, vert)

    write_object(vert_, text_, face)
