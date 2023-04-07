"""
    Author: Dan Billmann
    Date: 3/21/23

    Module to work with mediapipe face meshes.
"""
from pathlib import Path
from typing import Dict, List, Tuple, Union

import cv2
import mediapipe as mp
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmarkList
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmark
import numpy as np
from scipy.cluster.vq import kmeans2
from shapely import Polygon

from .utils import (
    get_keypoint_fpath,
    write_image,
)

# mediapipe utils
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh

drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
BOUNDARY_SPEC = mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=1, circle_radius=2)
MASK_COLOR = [255, 255, 255]


def add_keypoint_voxels(keypoints, voxels: np.ndarray):
    for k, v in keypoints.items():
        vx = voxels[v["index"]]
        keypoints[k]["voxel"] = vx
    return keypoints


def build_mask_from_boundary(
    img: np.ndarray, boundary: Union[Polygon, List[np.ndarray], np.ndarray]
) -> np.ndarray:
    """Returns black and whilte to represent the face outline."""
    overlay = img.copy()

    if isinstance(boundary, Polygon):
        int_coords = lambda x: np.array(x).round().astype(np.int32)
        boundary = [int_coords(boundary.exterior.coords)]

    elif isinstance(boundary, np.ndarray):
        # TODO: we might need to account for cv2's conventions here
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


def compute_keypoints(
    img: np.ndarray,
    landmarks: np.ndarray,
    landmark_spec=None,
):
    annotated_image = img.copy()
    mp_drawing.draw_landmarks(
        image=annotated_image,
        landmark_list=landmarks,
        connections=None,
        landmark_drawing_spec=landmark_spec,
    )

    return annotated_image, landmark_spec.color


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

    # if not write_image(fpath, annotated_image, **{"prefix": "boundary"}):
    #    print("WARNING: No image written.")

    return annotated_image, boundary_spec.color


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
    """Get the boundary IDs.

    I put the boundary IDs I found at the below URL into a hard-
    coded text file for simpler reads.

    https://github.com/tensorflow/
    tfjs-models/blob/838611c02f51159afdd77469ce67f0e26b7bbb23/
    face-landmarks-detection/src/mediapipe-facemesh/keypoints.ts
    """
    boundary = []
    with open("mediapipe_constants/boundary.txt") as bound:
        boundary = [int(x.strip()) for x in bound.readlines()]

    return boundary


def get_keypoint_indices(img: np.ndarray, color=Tuple[int, int, int]):
    idxs = get_color_indices_from_img(img, color)

    centroid, _ = kmeans2(idxs.astype(float), k=3, seed=0)
    # for i in range(3):
    #     print(centroid[i][0] * centroid[i][1])
    # 933816
    # 816185
    # 654454

    return centroid.astype(int), idxs


def find_keypoints(landmarks) -> None:
    """Get the coordinates of the 3 key points.

    See get_keypoint_idx() for more information.
    """
    idxs = get_keypoint_idx()
    marks = NormalizedLandmarkList()

    kp = {}  # ?
    for k, v in idxs.items():
        marks.landmark.append(landmarks.landmark[v])
        kp[k] = landmarks.landmark[v]  # ?
    return marks


def find_keypoint_indices(textures, keypoint_idxs):
    right_eye = ("right_eye", np.max(keypoint_idxs, axis=0))
    left_eye = ("left_eye", np.min(keypoint_idxs, axis=0))
    nosetip = ("nosetip", np.median(keypoint_idxs, axis=0))

    points = [right_eye, left_eye, nosetip]

    kp = {}
    for name, (row, col) in points:
        b = [row, col]
        aa = np.apply_along_axis(np.linalg.norm, 1, textures - b)
        idx = np.argmin(aa)
        kp[name] = {"index": idx}

    return kp


def get_keypoint_idx():
    """Get keypoint IDs

    https://github.com/tensorflow/
    tfjs-models/blob/838611c02f51159afdd77469ce67f0e26b7bbb23/
    face-landmarks-detection/src/mediapipe-facemesh/keypoints.ts

    Combined with this image:
    https://github.com/tensorflow/
    tfjs-models/blob/838611c02f51159afdd77469ce67f0e26b7bbb23/
    face-landmarks-detection/mesh_map.jpg
    """
    keypoints = {"left_eye_corner": 173, "right_eye_corner": 398, "nosetip": 1}

    return keypoints


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
