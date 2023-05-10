from pathlib import Path

from src.keypoints_ import run_keypoints
from src.pipeline import run_pipeline
from src.utils import parse_cli

if __name__ in "__main__":
    args = parse_cli()
    fpath_img = Path(args.image_path)
    fpath_obj = Path(args.object_path)
    fpath_bound = Path(args.boundary_path)
    if args.get("chunk_path"):
        fpath_chunk = Path(args.chunk_path)
    else:
        fpath_chunk = None

    if args.skip_boundary:
        run_keypoints(fpath_img=fpath_img, fpath_obj=fpath_obj)

    else:
        run_pipeline(
            fpath_img=fpath_img,
            fpath_obj=fpath_obj,
            fpath_bound=fpath_bound,
            fpath_chunk=fpath_chunk,
            debug=args.debug,
        )
