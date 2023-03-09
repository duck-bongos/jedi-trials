"""
    Author: Dan Billmann

    We are writing out .obj files with the masked vertices returned.
    These will be consumed downstream.
    
"""
from pathlib import Path
import re

from src.face_mesh import run_face_mesh_pipeline
from src.utils import parse_cli, process_obj_file

# https://github.com/tensorflow/tfjs-models/blob/838611c02f51159afdd77469ce67f0e26b7bbb23/face-landmarks-detection/src/mediapipe-facemesh/keypoints.ts


if __name__ == "__main__":
    args = parse_cli()
    source_img = Path(args.source_img)
    target_img = Path(args.target_img)
    source_obj = Path(args.source_obj)
    target_obj = Path(args.target_obj)

    process_obj_file(source_obj)
    run_face_mesh_pipeline(source_img, display=False)

    process_obj_file(target_obj)
    run_face_mesh_pipeline(target_img, display=False)
