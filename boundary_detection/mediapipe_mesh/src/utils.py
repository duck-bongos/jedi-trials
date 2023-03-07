from argparse import ArgumentParser
from pathlib import Path

from box import Box
import cv2
import numpy as np


def get_annotated_fpath(strpath: str, **kwargs) -> str:
    prefix = kwargs.get("prefix", "")
    suffix = kwargs.get("suffix", "")
    extension = kwargs.get("extension", "")

    fname = Path(strpath)
    dir = fname.stem
    name = fname.stem if prefix == "" else prefix + "_" + fname.stem
    name = fname.stem if suffix == "" else fname.stem + "_" + suffix

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
        "--target_img",
        "-t",
        dest="target_img",
        default="../../data/target/target.png",
        required=False,
    )
    args = ap.parse_args()
    args = Box(args.__dict__)

    return args


def write_image(fpath: str, img: np.ndarray, **kwargs) -> bool:
    """Save image as a png using cv2.imwrite."""
    # TODO: https://github.com/duck-bongos/jedi-trials/issues/1
    d = {"suffix": "img", "extension": "png"}
    d.update(kwargs)

    fpath_img = get_annotated_fpath(fpath, **d)
    return cv2.imwrite(fpath_img, img)


def write_matrix(fpath: str, matrix: np.ndarray, **kwargs) -> None:
    """Save as a numpy file in the annotated directory."""
    # np.save automatically adds a .npy path at the end, no extension needed
    d = {"suffix": "matrix"}
    d.update(kwargs)

    fpath_matrix = get_annotated_fpath(fpath, **d)
    np.save(fpath_matrix, matrix)


def write_object(
    fpath: str, index: np.ndarray, texture: np.ndarray, vertices: np.ndarray, **kwargs
) -> None:
    """Create an .obj file using the texture and vertices data."""
    d = {"prefix": "masked", "suffix": "object", "extension": "obj"}
    d.update(kwargs)

    fpath_selected = get_annotated_fpath(fpath, **d)

    with open(fpath_selected, "w") as s:
        # TODO: Should I include a 'material' .mtl file in the header?

        # write vertices (3D) first
        for line in vertices[index]:
            s.write(f"v {' '.join([str(s) for s in line])}\n")

        # write texture (2D) second
        for lin in texture[index]:
            s.write(f"vs {' '.join([str(s) for s in lin])}\n")
