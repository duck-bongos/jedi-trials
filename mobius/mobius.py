from cmath import atan, exp
from pathlib import Path
import sys

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


def mobius(z: complex, origin: complex, theta: float):
    i = complex(0, 1)
    z_ = exp(i * theta) * ((z - origin) / (1.0 - (origin.conjugate() * z)))
    return z_


def build_mobius_function(keypoints, textures):
    z1 = complex(*tuple(textures[keypoints["nosetip"], :]))
    z2 = complex(*tuple(textures[keypoints["left_eye"], :]))
    z3 = complex(*tuple(textures[keypoints["right_eye"], :]))

    origin = complex(0, 0)

    print(z1, z2, z3, origin)

    mb_le = (z2 - z1) / (1.0 - (z1.conjugate() * z2))
    mb_re = (z3 - z1) / (1.0 - (z1.conjugate() * z3))

    theta = atan((mb_re.imag - mb_le.imag) / (mb_le.real - mb_re.real))
    return theta


if __name__ in "__main__":
    if len(sys.argv) < 3:
        print("NO\n")

    vert, text, face = read_obj(sys.argv[1])
    keypoints = read_keypoints(sys.argv[2])

    build_mobius_function(keypoints, text)
