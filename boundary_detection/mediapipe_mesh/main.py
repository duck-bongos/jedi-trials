from pathlib import Path

from src.face_mesh import run_face_mesh_pipeline
from src.utils import parse_cli

# https://github.com/tensorflow/tfjs-models/blob/838611c02f51159afdd77469ce67f0e26b7bbb23/face-landmarks-detection/src/mediapipe-facemesh/keypoints.ts

if __name__ == "__main__":
    args = parse_cli()
    sp = Path(args.source_img).resolve().as_posix()
    tp = Path(args.target_img).resolve().as_posix()

    # this will compute and annotate
    run_face_mesh_pipeline(sp)
    run_face_mesh_pipeline(tp)

    # TODO: What are we trying to RETURN to the program for the next step?

    # 1. Quaternion matrix?
    # 2. Data files to be passed to ICP?
    # 3. ???
