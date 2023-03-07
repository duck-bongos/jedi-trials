"""
    Author: Dan Billmann

    We are writing out .obj files with the masked vertices returned.
    These will be consumed downstream.
    
"""
from pathlib import Path

from src.face_mesh import run_face_mesh_pipeline
from src.utils import parse_cli

# https://github.com/tensorflow/tfjs-models/blob/838611c02f51159afdd77469ce67f0e26b7bbb23/face-landmarks-detection/src/mediapipe-facemesh/keypoints.ts

if __name__ == "__main__":
    args = parse_cli()
    sp = Path(args.source_img).resolve().as_posix()
    tp = Path(args.target_img).resolve().as_posix()

    # this will compute and annotate
    run_face_mesh_pipeline(sp, display=False)
    run_face_mesh_pipeline(tp, display=False)
