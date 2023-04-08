"""
    Author: Dan Billmann
    Date: 3/21/23

    Module to work with mediapipe face meshes.
"""
from pathlib import Path
from typing import List, Tuple

import cv2
import mediapipe as mp
import numpy as np


from .face_mesh import (
    add_keypoint_voxels,
    build_mask_from_boundary,
    compute_boundary_edges,
    compute_face_mesh,
    compute_keypoints,
    compute_mesh_and_boundary,
    find_keypoint_indices,
    get_boundary_idx,
    get_boundary_from_annotation,
    get_keypoint_indices,
    find_keypoints,
)
from .utils import (
    preprocess_pixels,
    preprocess_voxels,
    process_obj_file,
    write_keypoints,
    write_object,
)

mp_drawing = mp.solutions.drawing_utils

BOUNDARY_SPEC = mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=1, circle_radius=2)
LANDMARK_SPEC = mp_drawing.DrawingSpec(
    color=(0, 0, 255), thickness=0.5, circle_radius=0.5
)
MASK_COLOR = [255, 255, 255]


def run_face_mesh_pipeline(
    fpath_img: Path, fpath_obj: Path, display=False
) -> Tuple[int, int]:
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

    # read from static list
    boundary_idx: List[int] = get_boundary_idx()
    boundary_contour: List[Tuple[int]] = compute_boundary_edges(boundary=boundary_idx)

    annotated_img, color = compute_mesh_and_boundary(
        img,
        landmarks,
        connections=boundary_contour,
        boundary_spec=BOUNDARY_SPEC,
    )

    boundary = get_boundary_from_annotation(annotated_img, color, two_d_only=True)

    # find the key points
    kp_img, kp_color = compute_keypoints(
        img, norm_keypoints, landmark_spec=BOUNDARY_SPEC
    )

    # QUCK CHECK
    # cv2.imwrite("keypoint.png", kp_img)

    # grab the key point indices
    kp_idx, all_idxs = get_keypoint_indices(kp_img, kp_color)

    # write out mask
    mask = build_mask_from_boundary(annotated_img, boundary)

    fpath_texture = fpath_img
    fpath_texture = fpath_texture.with_name(f"{fpath_img.stem}_texture.txt")
    texture_read = np.loadtxt(fpath_texture.resolve().as_posix())
    texture = texture_read.copy()

    # List of points of the form (y, x)
    texture[:, 0] *= img.shape[1]
    texture[:, 1] *= img.shape[0]
    texture = np.round(texture, 0).astype(int)

    texture_img = np.zeros(img.shape)
    for row, col in texture:
        texture_img[col, row] = MASK_COLOR

    # now merge with the mask, divide by 255 to return to 0-255 normal values.
    constrained_face = (texture_img * mask) // 255

    things = []
    for idx, (row, col) in enumerate(texture):
        # switch column and row
        if all(constrained_face[col, row] == MASK_COLOR):
            things.append(idx)

    keypoint_idxs = find_keypoint_indices(texture, kp_idx)

    # "C:\\Users\\dan\\Documents\\GitHub\\jedi-trials\\data\\tmp\\vertices3d.txt"
    idxs = np.array(things)
    fpath_voxel = fpath_img
    fpath_voxel = fpath_voxel.with_name(f"{fpath_voxel.stem}_voxels.txt")
    voxel_read = np.loadtxt(fpath_voxel.resolve().as_posix())
    voxels = voxel_read.copy()

    kpv = add_keypoint_voxels(keypoint_idxs, centered_voxels)
    write_keypoints(fpath_img, kpv)

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
