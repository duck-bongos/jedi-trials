"""
    Author: Dan Billmann
    Date: 3/21/23

    Module to work with mediapipe face meshes.
"""
from pathlib import Path
from typing import List, Tuple

import cv2
import mediapipe as mp
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmarkList
import numpy as np


from .face_mesh import (
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
from .utils import (
    preprocess_pixels,
    preprocess_voxels,
    process_obj_file,
    write_object,
    write_points,
)

mp_drawing = mp.solutions.drawing_utils

BOUNDARY_SPEC = mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=3, circle_radius=2)
# BOUNDARY_SPEC = mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=3, circle_radius=2)
LANDMARK_SPEC = mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=1, circle_radius=2)
# LANDMARK_SPEC = mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=5, circle_radius=5)
# BGR - RED Mask
MASK_COLOR = [0, 0, 255]


def find_boundary_points(landmarks, idxs):
    marks = NormalizedLandmarkList()
    for k in idxs:
        marks.landmark.append(landmarks.landmark[k])
    return marks


def run_face_mesh_pipeline(fpath_img: Path, fpath_obj: Path):
    # Convert the BGR image to RGB before processing?
    fpath_img_ = fpath_img.resolve().as_posix()
    img = cv2.imread(fpath_img_)
    img = img.copy()

    # process the file
    process_obj_file(fpath_obj)

    centered_voxels, _ = preprocess_voxels(fpath_obj, center=True, trim_z=0.875)
    centered_texture, _ = preprocess_pixels(fpath_obj)

    landmarks = compute_face_mesh(img)
    norm_keypoints = find_keypoints(landmarks)
    metric_idxs, norm_metric_points = find_metric_points(landmarks=landmarks)

    # read from static list
    boundary_idx: List[int] = get_boundary_idx()
    # bp = find_boundary_points(landmarks, boundary_idx)
    boundary_contour: List[Tuple[int]] = compute_boundary_edges(boundary=boundary_idx)

    annotated_img, color = compute_mesh_and_boundary(
        img,
        landmarks,
        connections=boundary_contour,
        boundary_spec=BOUNDARY_SPEC,
    )

    boundary = get_boundary_from_annotation(annotated_img, color, two_d_only=True)
    # black = np.zeros(img.shape)
    # black[boundary[:, 1], boundary[:, 0]] = color
    # cv2.imwrite("black.png", black)

    # fill = cv2.fillPoly(black, [boundary], color)
    # cv2.imwrite("filled_black.png", fill)

    # find the key points
    kp_img, kp_color = draw_points(img, norm_keypoints, landmark_spec=LANDMARK_SPEC)

    # find the metric points
    metric_img, metric_color = draw_points(
        img, norm_metric_points, landmark_spec=LANDMARK_SPEC
    )

    # b, c = draw_points(img, bp, LANDMARK_SPEC)
    # cv2.imwrite("b.png", b)

    # QUCK CHECK
    # cv2.imwrite("keypoint.png", kp_img)
    # cv2.imwrite("boundary.png", annotated_img)

    # grab the key point indices
    kp_idx = get_keypoint_centroids(
        kp_img, kp_color, k_size=len(norm_keypoints.landmark)
    )

    # grab the metric point indices
    mt_idx = get_keypoint_centroids(
        metric_img, metric_color, k_size=len(norm_metric_points.landmark)
    )

    # write out mask
    mask = build_mask_from_boundary(annotated_img, boundary)

    # write out mask to image
    # cv2.imwrite("binary_mask.png", mask)

    fpath_texture = fpath_img
    fpath_texture = fpath_texture.with_name(f"{fpath_img.stem}_texture.txt")
    texture_read = np.loadtxt(fpath_texture.resolve().as_posix())
    textures = texture_read.copy()

    # Understand the key points
    keypoint_texture_ids = find_keypoint_texture_ids(
        kp_idx, texture=textures, shape=img.shape
    )

    metric_point_texture_ids = find_metric_texture_idxs(
        metric_idxs, mt_idx, texture=textures, shape=img.shape
    )

    # List of points of the form (y, x) & scale them to image size
    textures[:, 0] *= img.shape[1]
    textures[:, 1] *= img.shape[0]
    textures = np.round(textures, 0).astype(int)

    texture_img = np.zeros(img.shape)
    for row, col in textures:
        texture_img[col, row] = MASK_COLOR

    # cv2.imwrite("texture_image.png", texture_img)

    # now merge with the mask, divide by 255 to return to 0-255 normal values.
    constrained_face = (texture_img * mask) // 255
    cf = (img * mask) // 255
    # cv2.imwrite("cf.png", cf)
    # cv2.imwrite("constrained_face.png", constrained_face)

    things = []
    for idx, (row, col) in enumerate(textures):
        # switch column and row
        # if constrained face's R coordinate is red, append
        if constrained_face[col, row][2] == 255:
            things.append(idx)

    # cv2.imwrite("constrained_textures.png", constrained_face)
    # ? keypoint_idxs = find_keypoint_indices(texture, kp_idx)

    # "C:\\Users\\dan\\Documents\\GitHub\\jedi-trials\\data\\tmp\\vertices3d.txt"
    idxs = np.array(things)
    # fpath_voxel = fpath_img
    # fpath_voxel = fpath_voxel.with_name(f"{fpath_voxel.stem}_voxels.txt")
    # voxel_read = np.loadtxt(fpath_voxel.resolve().as_posix())
    # voxels = voxel_read.copy()

    kpv = add_point_voxels(keypoint_texture_ids, centered_voxels)
    mpv = add_point_voxels(metric_point_texture_ids, centered_voxels)
    write_points(fpath_img, kpv)
    write_points(fpath_img, mpv, "metrics")

    write_object(
        fpath_out=fpath_img,
        fpath_obj=fpath_obj,
        index=idxs,
        texture=centered_texture,
        vertices=centered_voxels,
        keypoint_idxs=kp_idx,
    )
    #####################################

    return
