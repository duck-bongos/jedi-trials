"""Use quadric edge collapse decimation

    Author: Dan Billmann

    We need to reduce the density of the mesh

"""
from pathlib import Path
import sys
from typing import Dict, List, Optional, Union

import numpy as np
import pymeshlab

MS = pymeshlab.MeshSet()
M: np.ndarray
NT: np.ndarray
LE: np.ndarray
RE: np.ndarray


def get_collapsed_fpath(fname: Path, z: bool = True, **kwargs) -> str:
    extension = kwargs.get("extension", "")

    if z:
        data_dir = fname.parent.parent
    else:
        data_dir = fname.parent

    new_path = data_dir / "collapsed" / fname.name

    if extension != "":
        if "." in extension:
            new_path = new_path.with_suffix(extension)
        else:
            new_path = new_path.with_suffix(f".{extension}")

    return new_path.as_posix()


def find_new_points(kp: Dict[str, Dict[str, Union[np.ndarray, int]]]):
    vm = MS.current_mesh().vertex_matrix()

    for k, v in kp.items():
        voxel = v[:3]
        # Initialize the closest vertex index and distance
        # np.apply_along_axis(np.linalg.norm, 1, textures - b)
        dist = np.linalg.norm(vm - voxel, axis=1)
        smallest = np.argmin(dist)
        kp[k] = smallest

    return kp


def get_point_file(fpath_obj: Path, dir: str):
    data_dir = fpath_obj.parent.parent
    new_path = data_dir / dir / fpath_obj.stem
    new_path = new_path.with_suffix(".txt")
    return new_path


def get_dirpath_files(dirpath: Path, fpath_obj: Path, dir: str):
    new_path = dirpath / dir / fpath_obj.stem
    new_path = new_path.with_suffix(".txt")
    return new_path


def extract_points(lines: List[str]):
    keypoints = {}
    lines = [line.strip().split(" ") for line in lines]
    for l in lines:
        keypoints[l[0]] = np.array([float(i) for i in l[1:]])
    return keypoints


def read_points(fpath_obj: Path, dir: str, dirpath_points: Optional[Path] = None):
    if "source" in fpath_obj.as_posix():
        stem = "source.txt"

    else:
        stem = "target.txt"

    fpath_obj = fpath_obj.with_stem(stem)
    pfile = get_point_file(fpath_obj=fpath_obj, dir=dir)

    lines: List[str]
    with open(pfile) as f:
        lines = f.readlines()

    return extract_points(lines)


def qecd(fpath_obj: Path, targetfacenum: int = 30000):
    """Run QECD w/ textures, as per tutorial."""
    kp = read_points(fpath_obj=fpath_obj, dir="keypoints")
    mp = read_points(fpath_obj=fpath_obj, dir="metrics")

    NT = kp["nosetip"]
    LE = kp["left_eye"]
    RE = kp["right_eye"]

    MS.load_new_mesh(fpath_obj.as_posix())
    # M = MS.current_mesh().vertex_matrix()
    MS.meshing_decimation_quadric_edge_collapse_with_texture(
        targetfacenum=targetfacenum, preserveboundary=True
    )

    fpath_collapsed = get_collapsed_fpath(fpath_obj)
    # M = MS.current_mesh().vertex_matrix()

    new_kp = find_new_points(kp)
    new_mp = find_new_points(mp)

    write_points(new_kp, fpath_obj=fpath_obj, dir="keypoints")
    write_points(new_mp, fpath_obj=fpath_obj, dir="metrics")
    MS.save_current_mesh(fpath_collapsed)
    return


def write_points(
    keypoints: Dict[str, Dict[str, int]],
    fpath_obj: Path,
    dir: str,
):
    pfile = get_point_file(fpath_obj, dir)
    with open(pfile, "w") as f:
        for k, v in keypoints.items():
            f.write(f"{k} {v}\n")


if __name__ in "__main__":
    if len(sys.argv) == 2:
        qecd(fpath_obj=Path(sys.argv[1]))
    else:
        print("Usage: <qecd.py> <path_to_obj_file>")
        sys.exit(1)
