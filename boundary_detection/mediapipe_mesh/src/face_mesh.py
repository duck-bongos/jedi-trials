from pathlib import Path
from typing import List, Tuple

import cv2
import mediapipe as mp
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmarkList
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmark
import numpy as np

# mediapipe utils
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh

drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
BOUNDARY_SPEC = mp_drawing.DrawingSpec(
    color=(48, 255, 255), thickness=1, circle_radius=2
)


def compute_boundary_edges(boundary) -> List[Tuple[int, int]]:
    nl = []
    nl.append((boundary[len(boundary) - 1], boundary[0]))
    for i in range(0, len(boundary) - 1):
        nl.append((boundary[i], boundary[i + 1]))

    return frozenset(nl)


def compute_boundary_idx(mesh: np.ndarray):
    boundary = []
    with open("data/boundary.txt") as bound:
        boundary = [int(x.strip()) for x in bound.readlines()]

    return boundary


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


def draw_mesh(
    img: np.ndarray,
    landmarks: np.ndarray,
    fpath: str,
    prefix="",
    connections=None,
    boundary_spec=None,
) -> None:
    annotated_image = img
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
        mesh, landmarks = compute_face_mesh(img)
        # mesh_2d = mesh.copy()  # <-- I have to think about this still
        # mesh_2d[:, 2] = 0  # <-- I have to think about this still
        boundary_idx: List[int] = compute_boundary_idx(mesh)
        boundary_contour: List[Tuple[int]] = compute_boundary_edges(
            boundary=boundary_idx
        )
        write_mesh_points(mesh)
        write_mesh_points(mesh[boundary_idx], "boundary.obj")
        # boundary_landmarks = make_normalized_landmark_list(boundary_idx)

        if annotate:
            # draw_mesh(img, landmarks, fpath, prefix="mesh")
            # draw_mesh(img, mesh_2d)  # <-- I have to think about this still

            draw_mesh(
                img,
                landmarks,
                fpath,
                prefix="boundary",
                connections=boundary_contour,
                boundary_spec=BOUNDARY_SPEC,
            )

    return mesh, boundary_idx
