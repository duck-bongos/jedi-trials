"""Use quadric edge collapse decimation

    Author: Dan Billmann

    We need to reduce the density of the mesh

"""
from pathlib import Path
import sys

import pymeshlab

MS = pymeshlab.MeshSet()


def get_collapsed_fpath(fname: Path, **kwargs) -> str:
    extension = kwargs.get("extension", "")

    data_dir = fname.parent.parent
    new_path = data_dir / "collapsed" / fname.name

    if extension != "":
        if "." in extension:
            new_path = new_path.with_suffix(extension)
        else:
            new_path = new_path.with_suffix(f".{extension}")

    return new_path.as_posix()


def run_qecd(fpath_obj: Path, targetfacenum=50000) -> None:
    """Run QECD w/ textures, as per tutorial."""
    MS.load_new_mesh(fpath_obj.as_posix())
    MS.meshing_decimation_quadric_edge_collapse_with_texture(
        targetfacenum=targetfacenum, preserveboundary=True
    )
    collapsed = get_collapsed_fpath(fpath_obj)
    MS.save_current_mesh(collapsed)
    return


if __name__ in "__main__":
    if len(sys.argv) == 2:
        run_qecd(Path(sys.argv[1]))
    elif len(sys.argv) == 3:
        run_qecd(Path(sys.argv[1]), int(sys.argv[2]))
