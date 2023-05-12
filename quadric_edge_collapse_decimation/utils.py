"""Mostly file & IO operations."""
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np


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


def change_obj_path(fpath: Path):
    """Change the directory from 'boundary' to 'collapsed'."""
    fname = fpath.name
    top = fpath.parent.parent
    new_fpath = top / "collapsed" / fname
    return new_fpath


def change_important_point_path(fpath_ip: Path, fpath_obj: Path) -> Path:
    """Use the fpath_obj to change the fpath_ip."""
    new_name = (fpath_ip.parent / fpath_obj.name).with_suffix(".txt")
    return new_name


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


def write_points(keypoints: Dict[str, Dict[str, int]], fpath_out: Path):
    with open(fpath_out, "w+") as out:
        for k, v in keypoints.items():
            out.write(f"{k} {v}\n")


"""
def write_points(
    keypoints: Dict[str, Dict[str, int]],
    fpath_obj: Path,
    dir: str,
    dirpath: Optional[Path] = None,
):
    if not isinstance(dirpath, Path):
        with open(get_point_file(fpath_obj, dir), "w") as kp:
            for k, v in keypoints.items():
                kp.write(f"{k} {v}\n")
    else:
        with open(
            get_dirpath_files(dirpath=dirpath, fpath_obj=fpath_obj, dir=dir), "w"
        ) as kp:
            for k, v in keypoints.items():
                kp.write(f"{k} {v}\n")
"""
