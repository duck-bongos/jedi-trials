from collections import namedtuple
from pathlib import Path
from typing import List, Tuple

import cv2
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmarkList
import mediapipe as mp
import numpy as np


### CONSTANTS ###
# mediapipe utils
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh
##################

BOUNDARY_SPEC = mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=2)


class Boundary:
    """Small boundary class for capturing information"""

    def __init__(self, name: str, idxs: np.ndarray):
        self.name = name
        self.idxs = idxs


def compute_boundary_edges(boundary) -> List[Tuple[int, int]]:
    """Compute the closed loop of edges"""
    nl = []
    nl.append((boundary[len(boundary) - 1], boundary[0]))
    for i in range(0, len(boundary) - 1):
        nl.append((boundary[i], boundary[i + 1]))

    return nl


def compute_boundary_from_annotation(
    img: np.ndarray, boundary_color: Tuple[int, int, int], two_d_only: bool = False
) -> np.ndarray:
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

    # skip 3rd dimension
    boundary = boundary[:, :2]

    # deduplicate
    boundary = np.unique(boundary, axis=0)

    # try a reversal
    boundary[:, [0, 1]] = boundary[:, [1, 0]]

    # maybe this will help?
    return boundary


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


def get_boundary_idxs(path: Path) -> List[int]:
    boundary = []

    return boundary


def get_boundary(
    fpath_boundary: Path, fpath_img: Path, landmarks: NormalizedLandmarkList
) -> Boundary:
    # get image
    fpath_img_ = fpath_img.resolve().as_posix()
    img = cv2.imread(fpath_img_)
    img = img.copy()

    # get the boundary idxs
    idxs = get_boundary_idxs(fpath_boundary)

    # get the contour
    contour = compute_boundary_edges(boundary=idxs)

    # compute the mesh and boundary
    ai, c = compute_mesh_and_boundary(
        img=img, landmarks=landmarks, connections=contour, boundary_spec=BOUNDARY_SPEC
    )

    # return boundary from annotation
    boundary = compute_boundary_from_annotation(ai, c)

    b = Boundary(fpath_boundary.stem, boundary)
    return b
