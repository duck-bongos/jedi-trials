from pathlib import Path
from typing import Optional

import cv2
import mediapipe as mp
import numpy as np

from .boundary import Boundary, get_boundary
from .face_mesh import (
    add_point_voxels,
    compute_face_mesh,
    construct_mask,
    draw_points,
    find_keypoint_texture_ids,
    find_keypoints,
    find_metric_texture_idxs,
    find_metric_points,
    get_keypoint_centroids,
)
from .utils import (
    preprocess_pixels,
    preprocess_voxels,
    process_obj_file,
    write_points,
    write_object,
)

### CONSTANTS ###
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh
LANDMARK_SPEC = mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=1, circle_radius=2)
MASK_COLOR = (0, 255, 255)
#################


def run_pipeline(
    fpath_img: Path,
    fpath_obj: Path,
    fpath_boundary: Path,
    fpath_chunk: Optional[Path] = None,
    debug: bool = False,
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

    boundary: Boundary = get_boundary(
        fpath_boundary=fpath_boundary, fpath_img=fpath_img, landmarks=landmarks
    )
    mask: np.ndarray = construct_mask(
        img.shape, boundary=boundary.idxs, color=MASK_COLOR
    )

    if isinstance(fpath_chunk, Path):
        chunk: Boundary = get_boundary(
            fpath_boundary=fpath_chunk, fpath_img=fpath_img, landmarks=landmarks
        )

        # remove a chunk of the mask
        mask = cv2.fillPoly(mask, [chunk.idxs], (0, 0, 0))

    ################################
    ### COMPUTE IMPORTANT POINTS ###
    ################################
    # find the key points
    kp_img, kp_color = draw_points(img, norm_keypoints, landmark_spec=LANDMARK_SPEC)

    # find the metric point indices
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
    ################################
    ################################

    ################################
    ####### COMPUTE TEXTURES #######
    ################################
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

    kpv = add_point_voxels(keypoint_texture_ids, centered_voxels)
    mpv = add_point_voxels(metric_point_texture_ids, centered_voxels)

    # update the name
    fpath_img = fpath_img.with_name(f"{boundary.name}_{fpath_img.name}")
    if isinstance(fpath_chunk, Path):
        fpath_img = fpath_img.with_name(f"{chunk.name}_{fpath_img.name}")

    # write out important points
    write_points(fpath_img, kpv)
    write_points(fpath_img, mpv, "metrics")

    # List of points of the form (y, x) & scale them to image size
    textures[:, 0] *= img.shape[1]
    textures[:, 1] *= img.shape[0]
    textures = np.round(textures, 0).astype(int)

    texture_img = np.zeros(img.shape)
    for row, col in textures:
        texture_img[col, row] = MASK_COLOR
    ################################
    ################################

    ################################
    constrained_face = (texture_img * mask) // 255
    relevant_idxs = []
    for idx, (row, col) in enumerate(textures):
        # switch column and row
        # if constrained face's Red coordinate is 255, append
        if constrained_face[col, row][2] == 255:
            relevant_idxs.append(idx)

    # convert to numpy
    idxs = np.array(relevant_idxs)

    # write output
    write_object(
        fpath_out=fpath_img,
        fpath_obj=fpath_obj,
        index=idxs,
        texture=centered_texture,
        vertices=centered_voxels,
        keypoint_idxs=kp_idx,
    )
