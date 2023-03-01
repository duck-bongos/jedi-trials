from pathlib import Path
from typing import List, Tuple

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


def compute_boundary_edges(boundary) -> List[Tuple[int, int]]:
    nl = []
    nl.append((boundary[len(boundary) - 1], boundary[0]))
    for i in range(0, len(boundary) - 1):
        nl.append((boundary[i], boundary[i + 1]))

    return nl


def compute_face_mesh(img: np.ndarray):
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
        mesh: np.ndarray
        for mark in results.multi_face_landmarks:
            mesh = np.array([(m.x, m.y, m.z) for m in mark.landmark])
        return mesh, mark


def convert_mesh_to_idx(img: np.ndarray, mesh: np.ndarray) -> np.ndarray:
    """Convert the mediapipe output mesh to indices on the image.

    Mediapipe outputs an orthonormal mesh (range [-1, 1] in x, y, z directions) which is useful
    computationally but needs to be converted back to point indices for filtering purposes.
    TODO: (how) Do I make this generic across all boundary constraint methods?

    Args:
        img (np.ndarray): The input image.
        mesh (np.ndarray): The MediaPipe calculated orthonormal mesh.

    Returns:
        np.ndarray: An array with the index coordinates for each orthonormal point.

    """
    img = img.copy()

    # grab the origin point
    y_null = img.shape[0] // 2
    x_null = img.shape[1] // 2

    new_mesh = np.zeros(mesh.shape)

    new_mesh[:, 0] = np.round((mesh[:, 0] * y_null + y_null) / mesh[:, 2])
    new_mesh[:, 1] = np.round((mesh[:, 1] * x_null + x_null) / mesh[:, 2])

    return new_mesh


def get_boundary_idx():
    boundary = []
    with open("data/boundary.txt") as bound:
        boundary = [int(x.strip()) for x in bound.readlines()]

    return boundary


def draw_polygon(
    img: np.ndarray,
    landmarks: np.ndarray,
):
    # convert the landmark list to the
    img = img.copy()

    """    origin = (img.shape[1] // 2, img.shape[0] // 2)
    # tp1 = (1525, 1225)
    # tp2 = (1225, 1525)
    # tp3 = (289, 973)
    tp4 = (973, 289)
    # "origin"
    cv2.circle(img, center=origin, radius=10, color=(255, 255, 0))
    cv2.circle(img, center=(0, 0), radius=15, color=(255, 255, 0))
    cv2.circle(img, center=(img.shape[1], img.shape[0]), radius=15, color=(0, 255, 255))
    cv2.circle(img, center=tp4, radius=5, color=(255, 255, 255))"""
    # cv2.circle(img, center=tp4, radius=5, color=(0, 255, 255))

    """for x, y in marks:
        # img[x, y] = (255, 0, 0)

        cv2.circle(img, radius=5, center=(x, y), color=(255, 255, 0))
        cv2.circle(img, radius=5, center=(y, x), color=(255, 255, 255))"""
    landmarks[:, [0, 1]] = landmarks[:, [1, 0]]
    polygon = Polygon(landmarks)

    int_coords = lambda x: np.array(x).round().astype(np.int32)
    exterior = [int_coords(polygon.exterior.coords)]

    alpha = 0.1
    overlay = img.copy()
    cv2.fillPoly(overlay, exterior, color=(255, 255, 255))
    mask = get_color_indices_from_img(overlay, [255, 255, 255])
    cv2.fillPoly(overlay, exterior, color=(0, 255, 255))

    # cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
    cv2.imshow("Polygon", overlay)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return


def draw_mesh_and_boundary(
    img: np.ndarray,
    landmarks: np.ndarray,
    fpath: str,
    prefix="",
    connections=None,
    boundary_spec=None,
) -> None:
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

    return boundary


def get_color_indices_from_img(
    img: np.ndarray, color: Tuple[int, int, int], two_d_only: bool = False
):
    """Return the indices that match the color

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
    new_path = new_path.with_suffix(".png")
    return new_path.as_posix()


def make_normalized_landmark_list(mesh) -> NormalizedLandmarkList:
    l = []
    nll = NormalizedLandmarkList()
    l = [NormalizedLandmark(x=m[0], y=m[1], z=m[2]) for m in mesh]

    nll.landmark._values = l
    return nll


def write_mesh_points(mesh: np.ndarray, fname=""):
    fname = "face_mesh.obj" if fname == "" else fname
    with open(f"../../{fname}", "w+") as tt:
        for i in range(mesh.shape[0]):
            tt.write(f"v {mesh[i][0]} {mesh[i][1]} {mesh[i][2]}\n")
    return


def run_face_mesh_pipeline(fpath: str, compute=True, annotate=True) -> Tuple[int, int]:
    # Convert the BGR image to RGB before processing.
    img = cv2.imread(fpath)
    img = img.copy()

    if compute:
        ortho_mesh_landmarks, landmarks = compute_face_mesh(img)
        # mesh_2d = mesh.copy()  # <-- I have to think about this still
        # mesh_2d[:, 2] = 0  # <-- I have to think about this still
        boundary_idx: List[int] = get_boundary_idx()
        boundary_contour: List[Tuple[int]] = compute_boundary_edges(
            boundary=boundary_idx
        )

        # convert the orthonormal points back to usable coordinates
        # need to run on the LANDMARKS, which is "mesh"
        idx_mesh_landmarks = convert_mesh_to_idx(img, ortho_mesh_landmarks)
        # draw_polygon(            img,            landmarks=idx_mesh_landmarks,            boundary_idx=boundary_idx,        )

        write_mesh_points(ortho_mesh_landmarks)
        write_mesh_points(ortho_mesh_landmarks[boundary_idx], "boundary.obj")
        # boundary_landmarks = make_normalized_landmark_list(boundary_idx)

        if annotate:
            # draw_mesh(img, landmarks, fpath, prefix="mesh")
            # draw_mesh(img, mesh_2d)  # <-- I have to think about this still

            annotated_img, color = draw_mesh_and_boundary(
                img,
                landmarks,
                fpath,
                prefix="boundary",
                connections=boundary_contour,
                boundary_spec=BOUNDARY_SPEC,
            )

            boundary = get_boundary_from_annotation(
                annotated_img, color, two_d_only=True
            )

            draw_polygon(img=img, landmarks=boundary)

    return ortho_mesh_landmarks, boundary_idx
