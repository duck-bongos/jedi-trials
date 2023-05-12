from pathlib import Path
import sys
from typing import List

import numpy as np
import pymeshlab

MS = pymeshlab.MeshSet()
MT = pymeshlab.MeshSet()


def extract_points_from_file(lines: List[str]):
    keypoints = {}
    lines = [line.strip().split(" ") for line in lines]
    for l in lines:
        keypoints[l[0]] = np.array([float(x) for x in l[1:]])
    return keypoints


def read_important_points(fpath: Path):
    """Read key points and metric points"""
    with open(fpath) as f:
        lines = f.readlines()
    keypoints = extract_points_from_file(lines)
    return keypoints


def analyze(
    fpath_source: Path,
    fpath_target: Path,
    fpath_metric_source: Path,
    fpath_metric_target: Path,
):
    metric_s = read_important_points(fpath=fpath_metric_source)
    metric_t = read_important_points(fpath=fpath_metric_target)

    MS.load_new_mesh(fpath_source.as_posix())
    MT.load_new_mesh(fpath_target.as_posix())

    vms = MS.current_mesh().vertex_matrix()
    vmt = MT.current_mesh().vertex_matrix()
    total_distance = 0.0

    def distance(source: np.ndarray, target: np.ndarray):
        x = source[0] - target[0]
        y = source[1] - target[1]
        return np.sqrt((x * x) + (y * y))

    for k, v in metric_s.items():
        s_idx = int(metric_s[k][0])
        t_idx = int(metric_t[k][0])
        s = vms[s_idx]
        t = vmt[t_idx]
        d = distance(s, t)
        if k == "left_mouth_corner":
            print()

        total_distance += d
        print(f"{k}: {s_idx} {t_idx} | {d}")

    print(total_distance)
    print()


if __name__ in "__main__":
    fpath_source = Path(sys.argv[1])
    fpath_target = Path(sys.argv[2])
    fpath_metric_source = Path(sys.argv[3])
    fpath_metric_target = Path(sys.argv[4])

    analyze(fpath_source, fpath_target, fpath_metric_source, fpath_metric_target)
