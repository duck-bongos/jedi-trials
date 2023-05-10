"""
    Author: Dan Billmann
    Date: 4/20/23

    Module to extract keypoints
"""
from pathlib import Path
from typing import List, Tuple

import cv2
import mediapipe as mp
import numpy as np


from .face_mesh_ import (
    add_point_voxels,
    build_mask_from_boundary,
    compute_boundary_edges,
    compute_face_mesh,
    draw_points,
    compute_mesh_and_boundary,
    find_keypoint_texture_ids,
    find_keypoints,
    find_metric_points,
    find_metric_texture_idxs,
    get_boundary_idx,
    get_boundary_from_annotation,
    get_keypoint_centroids,
)
from .utils_ import (
    preprocess_pixels,
    preprocess_voxels,
    process_obj_file,
    write_object,
    write_points,
)

mp_drawing = mp.solutions.drawing_utils

BOUNDARY_SPEC = mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=1, circle_radius=2)
LANDMARK_SPEC = mp_drawing.DrawingSpec(
    color=(0, 0, 255), thickness=0.5, circle_radius=0.5
)
MASK_COLOR = [255, 255, 255]


def run_keypoints(fpath_img: Path, fpath_obj: Path):
    fpath_img_ = fpath_img.resolve().as_posix()
    img = cv2.imread(fpath_img_)
    img = img.copy()

    # process the file
    process_obj_file(fpath_obj)
    centered_voxels, _ = preprocess_voxels(fpath_obj, center=True, trim_z=0.875)

    landmarks = compute_face_mesh(img)
    norm_keypoints = find_keypoints(landmarks)
    metric_idxs, norm_metric_points = find_metric_points(landmarks=landmarks)

    # find the key points
    kp_img, kp_color = draw_points(img, norm_keypoints, landmark_spec=BOUNDARY_SPEC)

    # find the metric points
    metric_img, metric_color = draw_points(
        img, norm_metric_points, landmark_spec=BOUNDARY_SPEC
    )

    # grab the key point indices
    kp_idx = get_keypoint_centroids(
        kp_img, kp_color, k_size=len(norm_keypoints.landmark)
    )

    # grab the metric point indices
    mt_idx = get_keypoint_centroids(
        metric_img, metric_color, k_size=len(norm_metric_points.landmark)
    )

    # get textures
    fpath_texture = fpath_img
    fpath_texture = fpath_texture.with_name(f"{fpath_img.stem}_texture.txt")
    texture_read = np.loadtxt(fpath_texture.resolve().as_posix())
    textures = texture_read.copy()

    # Get the keypoint IDs
    keypoint_texture_ids = find_keypoint_texture_ids(
        kp_idx, texture=textures, shape=img.shape
    )

    metric_point_texture_ids = find_metric_texture_idxs(
        metric_idxs, mt_idx, texture=textures, shape=img.shape
    )

    kpv = add_point_voxels(keypoint_texture_ids, centered_voxels)
    mpv = add_point_voxels(metric_point_texture_ids, centered_voxels)

    # write out points
    write_points(fpath_img, kpv)
    write_points(fpath_img, mpv, "metrics")
