"""
"""

import re
import sys

import numpy as np
from numpy.linalg import norm


def read_obj(filename) -> np.ndarray:
    with open(filename, "r") as f:
        raw = f.read()

    lines = [line for line in re.findall("vt\ .*", raw)]

    lines_ = [
        tuple([float(i) for i in line[2:].strip().split(" ")])
        for line in re.findall("vt\ .*", raw)
    ]
    #     fl_lines = [(float(line[0]), float(line[1])) for line in str_lines]

    return np.array(lines_)


def knn(source: np.ndarray, target: np.ndarray):
    dist = norm(target[:, None, :] - source, axis=2)
    return np.argmin(dist, axis=0)


def map_points(source: np.ndarray, target: np.ndarray):
    mmm = {}
    for i, a in enumerate(source):
        min_id = -1
        min_dist = np.inf
        for j, b in enumerate(target):
            d = norm(b - a)
            if d < min_dist:
                min_id = j
                min_dist = d
        mmm[i] = min_id
    return mmm


def main():
    source = read_obj(sys.argv[1])
    target = read_obj(sys.argv[2])

    # nrr_map = knn(source, target)
    nrr_map = map_points(source, target)

    with open("../out/non-rigid_map.txt", "w") as nrr:
        for s, t in nrr_map:
            nrr.write(f"{s} {t}\n")


if __name__ in "__main__":
    main()
