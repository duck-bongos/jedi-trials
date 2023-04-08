from pathlib import Path
import sys


def read_keypoints(fpath: Path):
    keypoints = {}
    with open(fpath) as f:
        lines = f.readlines()[1:]
        lines = [line.split(" | ") for line in lines]

    keypoints = {k: int(v) for k, v in lines}
    return keypoints


def change_fname(fname: Path):
    name = fname.name
    data_dir = fname.parent.parent

    return data_dir / "transformed" / name


if __name__ in "__main__":
    if len(sys.argv) < 3:
        print("NO\n")

    keypoints = get_keypoints(sys.argv[2])
    print(keypoints)
