"""Use quadric edge collapse decimation

    Author: Dan Billmann

    We need to reduce the density of the mesh

"""
from pathlib import Path
import sys
from typing import Dict, Union

import numpy as np
import pymeshlab

MS = pymeshlab.MeshSet()


def get_collapsed_fpath(fname: Path, **kwargs) -> str:
    extension = kwargs.get("extension", "")

    data_dir = fname.parent.parent
    new_path = data_dir / "collapsed" / fname.name

    if extension != "":
        if "." in extension:
            new_path = new_path.with_suffix(extension)
        else:
            new_path = new_path.with_suffix(f".{extension}")

    return new_path.as_posix()


def find_new_keypoints(kp: Dict[str, Dict[str, Union[np.ndarray, int]]]):
    vm = MS.current_mesh().vertex_matrix()

    for k, v in kp.items():
        voxel = v[:3]
        # Initialize the closest vertex index and distance
        # np.apply_along_axis(np.linalg.norm, 1, textures - b)
        dist = np.apply_along_axis(np.linalg.norm, 1, vm - voxel)
        smallest = np.argmin(dist)
        kp[k] = smallest

    return kp


def get_keypoint_file(fpath_obj: Path):
    data_dir = fpath_obj.parent.parent
    new_path = data_dir / "keypoints" / fpath_obj.stem
    new_path = new_path.with_suffix(".txt")
    return new_path


def get_keypoints(fpath_obj: Path):
    keypoints = {}
    with open(get_keypoint_file(fpath_obj)) as kp:
        lines = kp.readlines()[1:]
        lines = [line.split(" | ") for line in lines]
        for l in lines:
            keypoints[l[0]] = np.array([float(i) for i in l[1].strip().split(" ")])

    return keypoints


def run_qecd(fpath_obj: Path, targetfacenum=50000) -> None:
    """Run QECD w/ textures, as per tutorial."""
    kp = get_keypoints(fpath_obj=fpath_obj)

    MS.load_new_mesh(fpath_obj.as_posix())
    MS.meshing_decimation_quadric_edge_collapse_with_texture(
        targetfacenum=targetfacenum, preserveboundary=True
    )

    fpath_collapsed = get_collapsed_fpath(fpath_obj)
    new_kp = find_new_keypoints(kp)
    write_keypoints(new_kp, fpath_obj=fpath_obj)

    MS.save_current_mesh(fpath_collapsed)
    return


def write_keypoints(keypoints: Dict[str, Dict[str, int]], fpath_obj: Path):
    with open(get_keypoint_file(fpath_obj), "w") as kp:
        kp.write(f"Name | Vertex ID\n")
        for k, v in keypoints.items():
            kp.write(f"{k} | {v}\n")


if __name__ in "__main__":
    if len(sys.argv) == 2:
        run_qecd(Path(sys.argv[1]))
    elif len(sys.argv) == 3:
        run_qecd(Path(sys.argv[1]), int(sys.argv[2]))
