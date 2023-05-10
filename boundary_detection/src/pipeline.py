"""
    Author: Dan Billmann
    Date: 3/21/23

    Module to work with mediapipe face meshes.
"""
from pathlib import Path
from typing import List, Tuple, Union

import cv2
import mediapipe as mp
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmarkList
import numpy as np

from .boundary import (
    Boundary,
    BoundarySet,
    compute_boundary_edges,
    compute_mesh_and_boundary,
    get_boundary_from_annotation,
)
from .face_mesh import (
    add_point_voxels,
    build_mask_from_boundary,
    compute_face_mesh,
    draw_points,
    find_keypoint_texture_ids,
    find_keypoints,
    find_metric_points,
    find_metric_texture_idxs,
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
MASK_COLOR = [0, 255, 255]


def compute_boundary(
    img: np.ndarray,
    boundary_idx,
    landmarks: NormalizedLandmarkList,
):
    boundary_contour: List[Tuple[int]] = compute_boundary_edges(boundary=boundary_idx)

    annot_img, color = compute_mesh_and_boundary(
        img,
        landmarks,
        connections=boundary_contour,
        boundary_spec=BOUNDARY_SPEC,
    )

    boundary = get_boundary_from_annotation(annot_img, color, two_d_only=True)

    return boundary


def run_face_mesh_pipeline(
    fpath_img: Path,
    fpath_obj: Path,
    boundaries: List[Union[Boundary, BoundarySet]],
    debug=False,
):
    # Convert the BGR image to RGB before processing?
    fpath_img_ = fpath_img.resolve().as_posix()
    img = cv2.imread(fpath_img_)
    img = img.copy()

    # process the file
    process_obj_file(fpath_obj)

    centered_voxels, _ = preprocess_voxels(fpath_obj, center=True, trim_z=0.6)
    centered_texture, _ = preprocess_pixels(fpath_obj)

    landmarks = compute_face_mesh(img)
    norm_keypoints = find_keypoints(landmarks)
    metric_idxs, norm_metric_points = find_metric_points(landmarks=landmarks)

    # find the key points
    kp_img, kp_color = draw_points(img, norm_keypoints, landmark_spec=LANDMARK_SPEC)

    # find the metric points
    metric_img, metric_color = draw_points(
        img, norm_metric_points, landmark_spec=LANDMARK_SPEC
    )

    # grab the key point indices
    kp_idx = get_keypoint_centroids(
        kp_img, kp_color, k_size=len(norm_keypoints.landmark)
    )

    # grab the metric point indices
    mt_idx = get_keypoint_centroids(
        metric_img, metric_color, k_size=len(norm_metric_points.landmark)
    )

    fpath_texture = fpath_img
    fpath_texture = fpath_texture.with_name(f"{fpath_img.stem}_texture.txt")
    texture_read = np.loadtxt(fpath_texture.resolve().as_posix())

    # repeate the following steps for each boundary
    chunks = []
    for bound in boundaries:
        if isinstance(bound, BoundarySet):
            chunks = bound.chunks
            bound = bound.boundary

        if isinstance(bound, Boundary):
            name = bound.name
            boundary_idx = bound.idxs
            chunks.append(bound)

        boundary = compute_boundary(img, boundary_idx=boundary_idx, landmarks=landmarks)

        for c in chunks:
            black = np.zeros(img.shape)

            black[boundary[:, 1], boundary[:, 0]] = MASK_COLOR
            # cv2.imwrite("black.png", black) if debug else print()
            mask = cv2.fillPoly(black, [boundary], MASK_COLOR)
            cv2.imwrite("mask.png", mask) if debug else print()

            if c.name != name:
                b = compute_boundary(img, boundary_idx=c.idxs, landmarks=landmarks)
                # take the chunk out
                chunk_removed = cv2.fillPoly(mask, [b], (0, 0, 0))
                cv2.imwrite(f"{c.name}_chunk_removed.png", chunk_removed)

                # cv2.imwrite("keypoint.png", kp_img) if debug else print()
                # cv2.imwrite("boundary.png", annotated_img) if debug else print()

                # write out mask
                # mask = build_mask_from_boundary(annotated_img, boundary)

                # write out mask to image
                # cv2.imwrite("binary_mask.png", mask) if debug else print()

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

            if c.name == name:
                cv2.imwrite(
                    f"{c.name}_texture_image.png", texture_img
                ) if debug else print()

            # now merge with the mask, divide by 255 to return to 0-255 normal values.
            if c.name != name:
                constrained_face = (texture_img * chunk_removed) // 255
            else:
                constrained_face = (texture_img * mask) // 255

            # cf = (img * mask) // 255
            # cv2.imwrite(f"{c.name}_cf.png", cf) if debug else print()
            cv2.imwrite(
                f"{c.name}_constrained_face.png", constrained_face
            ) if debug else print()

            relevant_idxs = []
            for idx, (row, col) in enumerate(textures):
                # switch column and row
                # if constrained face's R coordinate is red, append
                if constrained_face[col, row][2] == 255:
                    relevant_idxs.append(idx)

            idxs = np.array(relevant_idxs)
            kpv = add_point_voxels(keypoint_texture_ids, centered_voxels)
            mpv = add_point_voxels(metric_point_texture_ids, centered_voxels)

            # change write-out name
            fpath_img.with_name(f"{c.name}_{fpath_img.name}")

            # write everything
            write_points(fpath_img, kpv)
            write_points(fpath_img, mpv, "metrics")
            write_object(
                fpath_out=fpath_img,
                fpath_obj=fpath_obj,
                index=idxs,
                texture=centered_texture,
                vertices=centered_voxels,
                boundary_name=c.name,
            )
            #####################################

        return
