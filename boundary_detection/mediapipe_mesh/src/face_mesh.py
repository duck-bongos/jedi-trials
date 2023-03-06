from pathlib import Path
from typing import List, Tuple, Union

import cv2
import matplotlib.pyplot as plt
import mediapipe as mp
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmarkList
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmark
import numpy as np
from shapely import Point, Polygon

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


def create_polygon_from_landmarks(landmarks: List[float]) -> Polygon:
    return Polygon([Point(point.x, point.y) for point in landmarks])


def get_boundary_idx():
    boundary = []
    with open("data/boundary.txt") as bound:
        boundary = [int(x.strip()) for x in bound.readlines()]

    return boundary


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
    fpath = get_annotated_fpath(fpath, prefix=prefix)

    if not cv2.imwrite(fpath, annotated_image):
        print("NO image written.")

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


def get_annotated_fpath(strpath: str, prefix="") -> str:
    fname = Path(strpath)
    dir = fname.stem
    name = fname.stem if prefix == "" else prefix + "_" + fname.stem

    fpath = fname.parent.parent
    new_path = fpath / "annotated" / dir / name
    if prefix != "mask":
        new_path = new_path.with_suffix(".png")

    return new_path.as_posix()


def show_polygon_overlay(
    img: np.ndarray,
    landmarks: np.ndarray,
):
    """Draws a polygon on an image. For display purposes only."""
    # convert the landmark list to the
    img = img.copy()

    # TODO: candidate for refactor
    landmarks[:, [0, 1]] = landmarks[:, [1, 0]]
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


def write_mesh_points(mesh: np.ndarray, fpath=""):
    """Follows the standard defined at Wikipedia.

    ```
    >>> https://en.wikipedia.org/wiki/Wavefront_.obj_file

    #
        List of geometric vertices, with (x, y, z, [w]) coordinates, w is optional and defaults to 1.0.
        v 0.123 0.234 0.345 1.0
        v ...
    ```

    """
    with open(fpath, "w+") as tt:
        for i in range(mesh.shape[0]):
            tt.write(f"v {mesh[i][0]} {mesh[i][1]} {mesh[i][2]}\n")
    return


def write_out_image(fpath: str, mask: np.ndarray) -> None:
    """Save as a numpy file and cv2.imwrite to a png"""

    fpath_mask = get_annotated_fpath(fpath, "mask")
    np.save(fpath_mask, mask)

    # TODO: https://github.com/duck-bongos/jedi-trials/issues/1
    cv2.imwrite(fpath_mask.replace("mask", "mask_image") + ".png", mask)


def run_face_mesh_pipeline(fpath: str, compute=True, display=False) -> Tuple[int, int]:
    # Convert the BGR image to RGB before processing?
    img = cv2.imread(fpath)
    img = img.copy()

    if compute:
        landmarks = compute_face_mesh(img)
        # mesh_2d = mesh.copy()  # <-- I have to think about this still
        # mesh_2d[:, 2] = 0  # <-- I have to think about this still

        # read from static list
        boundary_idx: List[int] = get_boundary_idx()
        boundary_contour: List[Tuple[int]] = compute_boundary_edges(
            boundary=boundary_idx
        )

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
        # write_out_image(fpath=fpath, mask=mask)  #TODO: not cross-platform compatible

        # write out masked image
        masked_img = (mask * img) / mask.max()
        # write_out_image(fpath=fpath, mask=masked_img)  #TODO: not cross-platform compatible

        # write out mesh
        fpath_name = Path(fpath)
        name = (
            fpath_name.parent.parent
            / "annotated"
            / fpath_name.stem
            / f"masked_{fpath_name.stem}.obj"
        )
        write_mesh_points(masked_img, name)


        ### !!!! UNDER CONSTRUCTION !!!! ####
        two_d = np.loadtxt("C:\\Users\\dan\\Documents\\GitHub\\jedi-trials\\data\\tmp\\vertices2d.txt")
        two_d[:,0] *= img.shape[1]
        two_d[:,1] *= img.shape[0]
        two_d = np.round(two_d, 0).astype(int)

        things = []
        for idx, (row, col) in enumerate(two_d):
            if all(mask[row, col] == MASK_COLOR):
                things.append(idx)

        idxs = np.array(things)
        three_d = np.loadtxt("C:\\Users\\dan\\Documents\\GitHub\\jedi-trials\\data\\tmp\\vertices3d.txt")

        
        with open("C:\\Users\\dan\\Documents\\GitHub\\jedi-trials\\data\\annotated\\source\\selected.obj", 'w') as s:
            # write vertices first
            for line in three_d[idxs]:
                s.write(f"v {line}\n")
            
            # write texture second
            for lin in two_d[idxs]:
                s.write(f"vs {lin}\n")
        #####################################

        if display:
            show_polygon_overlay(img=img, landmarks=boundary)

    return
