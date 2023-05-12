"""Use quadric edge collapse decimation

    Author: Dan Billmann

    We need to reduce the density of the mesh

"""
from pathlib import Path
import sys
from typing import Dict, List, Optional, Union

import numpy as np
import pymeshlab

from utils import (
    change_important_point_path,
    change_obj_path,
    read_important_points,
    write_points,
)

MS = pymeshlab.MeshSet()


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


"""
def get_point_file(fpath_obj: Path, dir: str):
    data_dir = fpath_obj.parent.parent
    new_path = data_dir / dir / fpath_obj.stem
    new_path = new_path.with_suffix(".txt")
    return new_path


def get_dirpath_files(dirpath: Path, fpath_obj: Path, dir: str):
    new_path = dirpath / dir / fpath_obj.stem
    new_path = new_path.with_suffix(".txt")
    return new_path


def get_points(
    fpath_obj: Path,
    dir: str,
    dirpath_points: Optional[Path] = None,
):
    keypoints = {}
    if not isinstance(dirpath_points, Path):
        with open(get_point_file(fpath_obj, dir)) as kp:
            lines = kp.readlines()

    else:
        with open(
            get_dirpath_files(dirpath=dirpath_points, fpath_obj=fpath_obj, dir=dir)
        ) as kp:
            lines = kp.readlines()

    return keypoints
"""


def qecd(fpath_obj: Path, fpath_keypoints: Path, fpath_metrics: Path):
    # determine number of faces
    targetfacenum = 50000

    # read important points
    kp = read_important_points(fpath=fpath_keypoints)
    mp = read_important_points(fpath=fpath_metrics)

    # process mesh
    MS.load_new_mesh(fpath_obj.as_posix())
    MS.meshing_decimation_quadric_edge_collapse_with_texture(
        targetfacenum=targetfacenum, preserveboundary=True
    )

    new_kp = find_new_points(kp)
    new_mp = find_new_points(mp)

    new_fpath_keypoints = change_important_point_path(fpath_keypoints, fpath_obj)
    new_fpath_metrics = change_important_point_path(fpath_metrics, fpath_obj)

    write_points(new_kp, new_fpath_keypoints)
    write_points(new_mp, new_fpath_metrics)

    new_obj_path = change_obj_path(fpath_obj)
    print(new_obj_path.as_posix())
    print()
    MS.save_current_mesh(new_obj_path.as_posix())


if __name__ in "__main__":
    if len(sys.argv) != 4:
        print(f"Usage: qecd.py <path/to/file.obj> <path/to/keypoints.txt>. Exiting...")
        sys.exit(1)

    fpath_obj = Path(sys.argv[1])
    fpath_keypoints = Path(sys.argv[2])
    fpath_metrics = Path(sys.argv[3])

    print(
        f"Object: {fpath_obj}\nKeypoints: {fpath_keypoints}\nfpath_metrics: {fpath_metrics}"
    )
    qecd(
        fpath_obj=fpath_obj,
        fpath_keypoints=fpath_keypoints,
        fpath_metrics=fpath_metrics,
    )
