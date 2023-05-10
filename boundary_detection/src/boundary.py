from collections import namedtuple
from glob import glob
from typing import List, Tuple, Union

from box import Box
from mediapipe.framework.formats.landmark_pb2 import (
    NormalizedLandmark,
    NormalizedLandmarkList,
)
import mediapipe as mp
import numpy as np

# constants
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh

drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
Boundary = namedtuple("boundary", ("name", "idxs"))
BoundarySet = namedtuple("boundary_set", ("boundary", "chunks"))


def compute_boundary_edges(boundary) -> List[Tuple[int, int]]:
    nl = []
    nl.append((boundary[len(boundary) - 1], boundary[0]))
    for i in range(0, len(boundary) - 1):
        nl.append((boundary[i], boundary[i + 1]))

    return nl


def compute_mesh_and_boundary(
    img: np.ndarray,
    landmarks: np.ndarray,
    connections=None,
    boundary_spec=None,
) -> None:
    """Captures then writes out both mesh and boundary to file."""
    annotated_image = img.copy()
    connections = (
        mp_face_mesh.FACEMESH_TESSELATION if connections is None else connections
    )

    boundary_spec = (
        mp_drawing_styles.get_default_face_mesh_tesselation_style()
        if boundary_spec is None
        else boundary_spec
    )

    mp_drawing.draw_landmarks(
        image=annotated_image,
        landmark_list=landmarks,
        connections=connections,
        landmark_drawing_spec=None,
        connection_drawing_spec=boundary_spec,
    )

    return annotated_image, boundary_spec.color


def determine_boundary(
    cli_args: Box, c_override: bool = True
) -> List[Union[Boundary, BoundarySet]]:
    """Determine which boundaries you want to run against.

    Args:
        cli_args (Box): signals from the command line to determine which
                        boundary(ies) to use. Boundaries are found as a
                        list of text files at
                        `boundary_detection/[in]consistent_boundaries`
        c_override (bool): an override to ensure only consistent boundaries are run.

    Usage:
        outer: outer most consistent boundary.
        middle: middle circumference consistent boundary.
        inner: inner most circumference consistent boundary.
        custom: customized consistent boundary determined by the author.
        inconsistent: collect the set of inconsistent boundaries associated with
                    a consistent boundary.
    """
    boundaries: List[Boundary] = []

    options: Tuple[str] = ("outer", "middle", "inner", "custom", "inconsistent")
    opts = [getattr(cli_args, o) for o in options]

    inconsistent_boundary = False
    if opts[-1]:
        inconsistent_boundary = True

    # default to "custom"
    if not any(opts[:4]):
        b: Boundary = Boundary("custom", get_custom_boundary_idx())
        if inconsistent_boundary and c_override:
            bds = []
            # bds.append(b)
            incon_bds = get_inconsistent_boundaries(b.name)
            bds.extend(incon_bds)
            s = BoundarySet(b, bds)
            boundaries.append(s)
        else:
            boundaries.append(b)

    else:
        for opt in options[:4]:
            if getattr(cli_args, opt):
                b: Boundary = Boundary(opt, globals()[f"get_{opt}_boundary_idx"]())
                if inconsistent_boundary and c_override:
                    bds = []
                    # bds.append(b)
                    incon_bds = get_inconsistent_boundaries(opt)
                    bds.extend(incon_bds)
                    s = BoundarySet(b, bds)
                    boundaries.append(s)
                else:
                    boundaries.append(b)

    return boundaries


def find_boundary_points(landmarks, idxs):
    """Return the XYZ points in the boundary from their index."""
    marks = NormalizedLandmarkList()
    for k in idxs:
        marks.landmark.append(landmarks.landmark[k])
    return marks


def get_boundary_from_annotation(
    img: np.ndarray, boundary_color: Tuple[int, int, int], two_d_only: bool = False
):
    """Retrieve boundary

    ex:
        >>> boundary_spec
        DrawingSpec(color=(48, 255, 255), thickness=1, circle_radius=2)
        >>> boundary_spec.color
        (48, 255, 255)
        >>> boundary_color = boundary_spec.color
        >>> np.where(img == boundary_color)
        (array([ 289,  289,  ...53, 1535]), array([ 973,  973,  ...03,  809]), array([0, 1, 2, ..., 1, 2, 0]))
        >>> annotated_image[tmp[0][0], tmp[1][0]]
        array([ 48, 255, 255], dtype=uint8)

    """
    boundary_idx: Tuple[np.ndarray, np.ndarray] = np.where(
        (img == boundary_color).all(axis=2)
    )
    boundary: np.ndarray = np.column_stack(boundary_idx)

    if two_d_only:
        # skip 3rd dimension
        boundary = boundary[:, :2]

        # deduplicate
        boundary = np.unique(boundary, axis=0)

    # try a reversal
    boundary[:, [0, 1]] = boundary[:, [1, 0]]

    # maybe this will help?
    return boundary


def get_boundary_idx(fpath: str):
    """Get the boundary IDs.

    I put the boundary IDs I found at the below URL into a hard-
    coded text file for simpler reads.

    https://github.com/tensorflow/
    tfjs-models/blob/838611c02f51159afdd77469ce67f0e26b7bbb23/
    face-landmarks-detection/src/mediapipe-facemesh/keypoints.ts
    """
    boundary = []
    with open(fpath) as bound:
        boundary = [int(x.strip()) for x in bound.readlines()]

    return boundary


def get_custom_boundary_idx():
    """A combination of middle.txt and inner.txt"""
    return get_boundary_idx("consistent_boundaries/custom.txt")


def get_inner_boundary_idx():
    return get_boundary_idx("consistent_boundaries/inner.txt")


def get_inconsistent_boundaries(name: str) -> List[Boundary]:
    """Retrieve all inconsistent boundaries associated with the name."""
    ib = []
    for f in glob(f"inconsistent_boundaries/{name}/*.txt"):
        idx: List[int] = get_boundary_idx(f)
        name = f.split("/")[-1].split(".")[0]
        b = Boundary(name, idx)
        ib.append(b)

    return ib


def get_middle_boundary_idx():
    return get_boundary_idx("consistent_boundaries/middle.txt")


def get_outer_boundary_idx():
    return get_boundary_idx("consistent_boundaries/outer.txt")
