from argparse import ArgumentParser
from pathlib import Path
import re
from typing import List, Set

from box import Box
import cv2
import numpy as np


def get_annotated_fpath(fname: Path, **kwargs) -> str:
    prefix = kwargs.get("prefix", "")
    suffix = kwargs.get("suffix", "")
    extension = kwargs.get("extension", "")

    dir = fname.stem
    name = fname.stem if prefix == "" else prefix + "_" + fname.stem
    name = name if suffix == "" else name + "_" + suffix

    fpath = fname.parent.parent
    new_path = fpath / "annotated" / dir / name

    if extension != "":
        if "." in extension:
            new_path = new_path.with_suffix(extension)
        else:
            new_path = new_path.with_suffix(f".{extension}")

    return new_path.as_posix()


def parse_cli() -> ArgumentParser:
    ap = ArgumentParser()
    ap.add_argument(
        "--source_img",
        "-s",
        dest="source_img",
        default="../../data/source/source.png",
        required=False,
    )
    ap.add_argument(
        "--source_obj",
        "-so",
        dest="source_obj",
        default="../../data/source/source.obj",
        required=False,
    )
    ap.add_argument(
        "--target_img",
        "-t",
        dest="target_img",
        default="../../data/target/target.png",
        required=False,
    )
    ap.add_argument(
        "--target_obj",
        "-to",
        dest="target_obj",
        default="../../data/target/target.obj",
        required=False,
    )
    args = ap.parse_args()
    args = Box(args.__dict__)

    return args


def process_obj_file(in_fpath: Path):
    """Split the input .obj file into voxel and texture files.

    In order to know which voxel (3D) points we're manipulating,
    we also need to know the corresponding texture (2D) points.
    These are neatly organized by index in a Wavefront (.obj) file.
    According to Wikipedia's page on formatting Wavefront files
    (https://en.wikipedia.org/wiki/Wavefront_.obj_file), there is
    a clean way of parsing out the voxels from the texture points
    using regular expressions.
    """
    voxel_re = re.compile("v\ ")
    texture_re = re.compile("vt\ ")

    dirpath_out = in_fpath
    fname_voxel = dirpath_out.with_name(f"{in_fpath.stem}_voxels.txt")
    fname_texture = dirpath_out.with_name(f"{in_fpath.stem}_texture.txt")

    with open(in_fpath.resolve().as_posix(), "r") as f:
        with open(fname_voxel.resolve().as_posix(), "w") as two, open(
            fname_texture.resolve().as_posix(), "w"
        ) as three:
            for line in f.readlines():
                if voxel_re.search(line):
                    two.write(f"{line[2:]}")

                if texture_re.search(line):
                    three.write(f"{line[3:]}")


def write_image(fpath: Path, img: np.ndarray, **kwargs) -> bool:
    """Save image as a png using cv2.imwrite."""
    # TODO: https://github.com/duck-bongos/jedi-trials/issues/1
    d = {"suffix": "img", "extension": "png"}
    d.update(kwargs)

    fpath_img = get_annotated_fpath(fpath, **d)
    return cv2.imwrite(fpath_img, img)


def write_matrix(fpath: Path, matrix: np.ndarray, **kwargs) -> None:
    """Save as a numpy file in the annotated directory."""
    # np.save automatically adds a .npy path at the end, no extension needed
    d = {"suffix": "matrix"}
    d.update(kwargs)

    fpath_matrix = get_annotated_fpath(fpath, **d)
    np.save(fpath_matrix, matrix)


def write_object(
    fpath_out: Path,
    fpath_obj: Path,
    index: np.ndarray,
    texture: np.ndarray,
    vertices: np.ndarray,
    **kwargs,
) -> None:
    """Create an .obj file using the texture and vertices data."""
    d = {"prefix": "masked", "suffix": "object", "extension": "obj"}
    d.update(kwargs)
    indices_min = min(index)

    get_vertex_indices = lambda a: set(int(i) for i in re.split("f| |/", a[2:]))

    fpath_selected = get_annotated_fpath(fpath_out, **d)

    with open(fpath_selected, "w") as s:
        # TODO: Should I include a 'material' .mtl file in the header?

        # write vertices (3D) first
        for line in vertices[index]:
            s.write(f"v {' '.join([str(s) for s in line])}\n")

        # write texture (2D) second
        for lin in texture[index]:
            s.write(f"vs {' '.join([str(s) for s in lin])}\n")

        with open(fpath_obj, "r") as f_obj:
            read = f_obj.read()
            faces = re.findall("f.*", read)
            # for every face object...
            vertices_of_faces = [get_vertex_indices(f) for f in faces]
            for face_idxs in vertices_of_faces:
                if min(face_idxs) >= indices_min:
                    # if all the vertex indices of the face are in the boundary
                    if len(face_idxs) == len(face_idxs.intersection(set(index))):
                        # write out the line to the new file
                        s_out = "f " + " ".join([f"{i}/{i}" for i in face_idxs]) + "\n"
                        s.write(s_out)
