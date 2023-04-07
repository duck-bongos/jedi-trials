"""
    Author: Dan Billmann

    We are writing out .obj files with the masked vertices returned.
    These will be consumed downstream.
    
"""
from pathlib import Path

from src.pipeline import run_face_mesh_pipeline
from src.utils import parse_cli


if __name__ == "__main__":
    args = parse_cli()
    fpath_source_img = Path(args.source_img)
    fpath_target_img = Path(args.target_img)
    fpath_source_obj = Path(args.source_obj)
    fpath_target_obj = Path(args.target_obj)

    run_face_mesh_pipeline(
        fpath_img=fpath_source_img, fpath_obj=fpath_source_obj, display=False
    )

    run_face_mesh_pipeline(
        fpath_img=fpath_target_img, fpath_obj=fpath_target_obj, display=False
    )

    print("Boundary detection complete.")
