from cmath import atan, exp, phase, pi, rect, sqrt
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


def build_mobius_function(keypoints, textures):
    z1 = complex(*tuple(textures[keypoints["nosetip"], :]))
    z2 = complex(*tuple(textures[keypoints["left_eye"], :]))
    z3 = complex(*tuple(textures[keypoints["right_eye"], :]))

    mb_le = (z2 - z1) / (1.0 - (z1.conjugate() * z2))
    mb_re = (z3 - z1) / (1.0 - (z1.conjugate() * z3))

    theta = atan((mb_re.imag - mb_le.imag) / (mb_le.real - mb_re.real))
    theta = -principal_arg(z2 - z1)
    ang = np.angle(z2 - z1 / (z3 - z1))
    return z1, theta


def t(z):
    z - z3


if __name__ in "__main__":
    if len(sys.argv) < 3:
        print("NO\n")
        sys.exit(1)

    vert, text, face = read_obj(sys.argv[1])
    keypoints = read_keypoints(sys.argv[2])

    origin, theta = build_mobius_function(keypoints, text)
    z1 = complex(*tuple(text[keypoints["left_eye"]]))
    z2 = complex(*tuple(text[keypoints["right_eye"]]))
    z3 = complex(*tuple(text[keypoints["nosetip"]]))

    w1 = complex(-1, 1) / (2 * sqrt(2))
    w2 = complex(+1, 1) / (2 * sqrt(2))
    w3 = complex(0, 0)

    print(f"{z1} -> {w1}\n{z2} -> {w2}\n{z3} -> {w3}")
    for v in vert:
        mobius(v[:3], origin, theta)
