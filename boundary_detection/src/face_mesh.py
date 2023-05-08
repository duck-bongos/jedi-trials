"""
    Author: Dan Billmann
    Date: 3/21/23

    Module to work with mediapipe face meshes.
"""
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

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
# BOUNDARY_SPEC = mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=1, circle_radius=2)
BOUNDARY_SPEC = mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=2)
MASK_COLOR = [0, 255, 255]


def add_point_voxels(keypoints, voxels: np.ndarray):
    for k, v in keypoints.items():
        vx = voxels[v["idx"]]
        keypoints[k]["xyz"] = np.round(vx, 5)
    return keypoints


def build_mask_from_boundary(
    img: np.ndarray,
    boundary: Union[Polygon, List[np.ndarray], np.ndarray],
    color: Optional[List[int]] = None,
) -> np.ndarray:
    """Returns black and whilte to represent the face outline."""
    overlay = img.copy()
    color = color if color is not None else MASK_COLOR

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


def draw_points(
    img: np.ndarray,
    landmarks: NormalizedLandmarkList,
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


def find_keypoints(landmarks) -> NormalizedLandmarkList:
    """Get the coordinates of the 3 key points.

    See get_keypoint_idx() for more information.
    """
    idxs = get_keypoint_idx()
    marks = NormalizedLandmarkList()
    for k in idxs:
        marks.landmark.append(landmarks.landmark[k])
    return marks


def find_metric_points(landmarks) -> NormalizedLandmarkList:
    """Return coordinates of all metric points

    See metric_idx() for more information.
    """
    mp: Dict[str, int]
    idxs: List[int]
    mp, idxs = get_metric_idx()
    marks = NormalizedLandmarkList()
    for i in idxs:
        marks.landmark.append(landmarks.landmark[i])
    return mp, marks


def find_boundary_points(landmarks, idxs):
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


def get_boundary_idx():
    """Get the boundary IDs.

    I put the boundary IDs I found at the below URL into a hard-
    coded text file for simpler reads.

    https://github.com/tensorflow/
    tfjs-models/blob/838611c02f51159afdd77469ce67f0e26b7bbb23/
    face-landmarks-detection/src/mediapipe-facemesh/keypoints.ts
    """
    boundary = []
    with open("mediapipe_constants/silhouette.txt") as bound:
        boundary = [int(x.strip()) for x in bound.readlines()]

    return boundary


def get_second_boundary_idx():
    boundary = []
    with open("mediapipe_constants/second.txt") as bound:
        boundary = [int(x.strip()) for x in bound.readlines()]
    return boundary


def get_third_boundary_idx():
    boundary = []
    with open("mediapipe_constants/third.txt") as bound:
        boundary = [int(x.strip()) for x in bound.readlines()]
    return boundary


def get_custom_boundary_idx():
    """A combination of second.txt and third.txt"""
    boundary = []
    with open("mediapipe_constants/custom.txt") as bound:
        boundary = [int(x.strip()) for x in bound.readlines()]
    return boundary


def get_keypoint_idx() -> List[int]:
    """Get keypoint IDs

    https://github.com/tensorflow/
    tfjs-models/blob/838611c02f51159afdd77469ce67f0e26b7bbb23/
    face-landmarks-detection/src/mediapipe-facemesh/keypoints.ts

    Combined with this image:
    https://github.com/tensorflow/
    tfjs-models/blob/838611c02f51159afdd77469ce67f0e26b7bbb23/
    face-landmarks-detection/mesh_map.jpg
    """
    # keypoints = {"left_eye_corner": 173, "right_eye_corner": 398, "nosetip": 1}
    keypoints = [
        1,
        173,
        398,
    ]

    return keypoints


def get_metric_idx() -> Tuple[Dict[str, int], List[int]]:
    """"""
    lines = []
    with open("mediapipe_constants/metrics.txt") as m:
        lines = m.readlines()

    points = {line.strip().split(" ")[0]: line.strip().split(" ")[1] for line in lines}
    metrics = [int(line.strip().split(" ")[1]) for line in lines]
    return points, metrics


def get_keypoint_centroids(img: np.ndarray, color=Tuple[int, int, int], k_size=1):
    idxs = get_color_indices_from_img(img, color)
    arr = np.zeros((k_size, 2))
    for i in range(k_size):
        arr[i] = idxs[i * 8 : (i + 1) * 8].mean(axis=0)

    arr = np.round(arr, 0).astype(int)

    return arr


def find_keypoint_texture_ids(
    keypoint_idx: np.ndarray, texture: np.ndarray, shape: tuple
):
    """"""
    kpi = np.zeros(keypoint_idx.shape)
    kpi[:, 0] = keypoint_idx[:, 0] / shape[0]
    kpi[:, 1] = keypoint_idx[:, 1] / shape[1]

    nt_idx = np.argmax(kpi[:, 0])
    le_idx = np.argmin(kpi[:, 1])
    re_idx = np.argmax(kpi[:, 1])
    kpi[:, [0, 1]] = kpi[:, [1, 0]]
    d = {}
    d["nosetip"] = {}
    d["left_eye"] = {}
    d["right_eye"] = {}
    d["nosetip"]["uv"] = kpi[nt_idx, :]
    d["left_eye"]["uv"] = kpi[le_idx, :]
    d["right_eye"]["uv"] = kpi[re_idx, :]

    for k, v in d.items():
        distance = np.linalg.norm(texture - v["uv"], axis=1)
        d[k]["idx"] = np.argmin(distance)

    return d


def find_metric_texture_idxs(
    points: Dict[str, int],
    metric_idx: np.ndarray,
    texture: np.ndarray,
    shape: Tuple[int, int],
):
    mi = np.zeros(metric_idx.shape)
    mi[:, 0] = metric_idx[:, 0] / shape[0]
    mi[:, 1] = metric_idx[:, 1] / shape[1]

    for i, (k, v) in enumerate(points.items()):
        points[k] = {}
        points[k]["mark"] = int(v)
        points[k]["uv"] = mi[i]
        d = np.linalg.norm(texture - mi[i], axis=1)
        points[k]["idx"] = np.argmin(d)

    return points


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
