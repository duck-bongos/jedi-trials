from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path
from typing import List, Tuple, Union

import cv2
import matplotlib.pyplot as plt
import mediapipe as mp
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmarkList
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmark
from numba import njit, vectorize
import numpy as np
from pywavefront import Wavefront
from shapely import Point, Polygon

from .utils import get_annotated_fpath, write_image, write_matrix, write_object


# mediapipe utils
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh

drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
BOUNDARY_SPEC = mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=1, circle_radius=2)
MASK_COLOR = [255, 255, 255]


def build_mask_from_boundary(
    img: np.ndarray, boundary: Union[Polygon, List[np.ndarray], np.ndarray]
) -> np.ndarray:
    """Returns black and whilte to represent the face outline."""
    overlay = img.copy()

    if isinstance(boundary, Polygon):
        int_coords = lambda x: np.array(x).round().astype(np.int32)
        boundary = [int_coords(boundary.exterior.coords)]

    elif isinstance(boundary, np.ndarray):
        #TODO: we might need to account for cv2's conventions here
        # # boundary[:, [0,1]] = boundary[:, [1,0]]
        boundary = [boundary]

    mask = cv2.fillPoly(overlay, boundary, color=MASK_COLOR)

    # white mask
    idx = get_color_indices_from_img(mask, MASK_COLOR)

    z = np.zeros(img.shape)
    z[idx[:, 0], idx[:, 1]] = MASK_COLOR

    return z


def compute_boundary_edges(boundary) -> List[Tuple[int, int]]:
    nl = []
    nl.append((boundary[len(boundary) - 1], boundary[0]))
    for i in range(0, len(boundary) - 1):
        nl.append((boundary[i], boundary[i + 1]))

    return nl


def compute_face_mesh(img: np.ndarray):
    """Compute the face mesh using mediapipe.

    We need to use the variable "mark" and the landmarks list isn't indexable or iterable
    so we just return it immediately."""
    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
    ) as face_mesh:
        results = face_mesh.process(img)
        # results = face_mesh.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        if not results.multi_face_landmarks:
            return -1

        # multi_face_landmarks is a non-iterable, non-indexible list of 1 item
        for mark in results.multi_face_landmarks:
            return mark


def compute_mesh_and_boundary(
    img: np.ndarray,
    landmarks: np.ndarray,
    fpath: str,
    prefix="",
    connections=None,
    boundary_spec=None,
) -> None:
    """Writes out mesh and boundary to file."""
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

    if not write_image(fpath, annotated_image, **{"prefix": "boundary"}):
        print("NO image written.")

    return annotated_image, boundary_spec.color


def create_polygon_from_landmarks(landmarks: List[float]) -> Polygon:
    return Polygon([Point(point.x, point.y) for point in landmarks])


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


def get_boundary_idx():
    boundary = []
    with open("data/boundary.txt") as bound:
        boundary = [int(x.strip()) for x in bound.readlines()]

    return boundary


def get_color_indices_from_img(
    img: np.ndarray, color: Tuple[int, int, int], two_d_only: bool = False
):
    """Return the indices that match the color.

    ex:
        >>> boundary_spec
        DrawingSpec(color=(48, 255, 255), thickness=1, circle_radius=2)
        >>> boundary_spec.color
        (48, 255, 255)
        >>> color = boundary_spec.color
        >>> np.where(img == color)
        (array([ 289,  289,  ...53, 1535]), array([ 973,  973,  ...03,  809]), array([0, 1, 2, ..., 1, 2, 0]))
        >>> annotated_image[tmp[0][0], tmp[1][0]]
        array([ 48, 255, 255], dtype=uint8)

    """
    boundary_idx: Tuple[np.ndarray, np.ndarray] = np.where((img == color).all(axis=2))
    boundary: np.ndarray = np.column_stack(boundary_idx)

    if two_d_only:
        # skip 3rd dimension
        boundary = boundary[:, :2]

        # deduplicate
        boundary = np.unique(boundary, axis=0)

    return boundary


def show_polygon_overlay(
    img: np.ndarray,
    landmarks: np.ndarray,
):
    """Draws a polygon on an image. For display purposes only."""
    # convert the landmark list to the
    img = img.copy()

    # TODO: candidate for refactor
    # landmarks[:, [0, 1]] = landmarks[:, [1, 0]]  # correct for CV2 interpretation
    polygon = Polygon(landmarks)
    int_coords = lambda x: np.array(x).round().astype(np.int32)
    exterior = [int_coords(polygon.exterior.coords)]

    alpha = 0.1
    overlay = img.copy()
    cv2.fillPoly(overlay, exterior, color=(0, 255, 255))

    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
    cv2.imshow("Polygon", overlay)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return


def run_face_mesh_pipeline(fpath: str, compute=True, display=False) -> Tuple[int, int]:
    # Convert the BGR image to RGB before processing?
    img = cv2.imread(fpath)
    img = img.copy()

    if compute:
        # These landmarks are ORTHONORMAL
        landmarks = compute_face_mesh(img)

        # read from static list
        boundary_idx: List[int] = get_boundary_idx()

        # Create a contour
        boundary_contour: List[Tuple[int]] = compute_boundary_edges(
            boundary=boundary_idx
        )

        # Get an annotated image and the boundary color
        annotated_img, color = compute_mesh_and_boundary(
            img,
            landmarks,
            fpath,
            prefix="boundary",
            connections=boundary_contour,
            boundary_spec=BOUNDARY_SPEC,
        )

        boundary = get_boundary_from_annotation(annotated_img, color, two_d_only=True)

        # write out mask
        mask = build_mask_from_boundary(annotated_img, boundary)
        write_matrix(
            fpath=fpath, matrix=mask, **{"prefix": "masked"}
        )  # TODO: not cross-platform compatible
        write_image(fpath, mask, **{"prefix": "masked", "suffix": "matrix_img"})

        # write out masked image
        masked_img = (mask * img) / mask.max()
        write_image(
            fpath=fpath, img=masked_img, **{"prefix": "masked", "suffix": "img"}
        )  # TODO: not cross-platform compatible

        # TODO: WHY? - write out mesh
        # fpath_mesh = get_annotated_fpath(fpath, prefix="masked", suffix="", extension="obj")
        # write_mesh_points(masked_img, fpath_mesh)

        # ? Can I create my own?

        ### !!!! UNDER CONSTRUCTION !!!! ####

        # Of the form (y, x)
        two_d = np.loadtxt(
            "C:\\Users\\dan\\Documents\\GitHub\\jedi-trials\\data\\tmp\\vertices2d.txt"
        )
        texture = two_d.copy()
        texture[:, 0] *= img.shape[1]
        texture[:, 1] *= img.shape[0]
        texture = np.round(texture, 0).astype(int)

        # !!! TODO: https://github.com/duck-bongos/jedi-trials/issues/3
        two_test = np.zeros(img.shape)
        for row, col in texture:
            two_test[col, row] = MASK_COLOR

        write_image(
            "C:\\Users\\dan\\Documents\\GitHub\\jedi-trials\\data\\tmp\\vertices2d.txt",
            two_test,
            **{"prefix": "object_mask", "extension": "png"},
        )

        # now merge with the mask
        constrained_face = (two_test * mask) // 255
        write_image(
            "C:\\Users\\dan\\Documents\\GitHub\\jedi-trials\\data\\tmp\\vertices2d.txt",
            constrained_face,
            **{"prefix": "object_mask", "suffix": "merge_test", "extension": "png"},
        )
        # !!!

        things = []
        for idx, (row, col) in enumerate(texture):
            # switch column and row
            if all(constrained_face[col, row] == MASK_COLOR):
                things.append(idx)

        idxs = np.array(things)
        three_d = np.loadtxt(
            "C:\\Users\\dan\\Documents\\GitHub\\jedi-trials\\data\\tmp\\vertices3d.txt"
        )

        # TODO remove 301-305?
        # re-normalize the 2D points
        # two_d = two_d.astype(float)
        # two_d[:, 0] /= img.shape[0]
        # two_d[:, 1] /= img.shape[1]
        # two_d = np.round(two_d, 7)  # the input file was rounded to 2 decimals

        write_object(fpath, idxs, texture=two_d, vertices=three_d)
        #####################################

        if display:
            show_polygon_overlay(img=img, landmarks=boundary)

    return
