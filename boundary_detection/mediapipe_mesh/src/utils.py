from argparse import ArgumentParser

from box import Box


def parse_cli() -> ArgumentParser:
    ap = ArgumentParser()
    ap.add_argument(
        "--source_img",
        "-s",
        dest="source_img",
        default="../../data/source/source.png",
        required=False,
    )
    ap.add_argument(
        "--target_img",
        "-t",
        dest="target_img",
        default="../../data/target/target.png",
        required=False,
    )
    args = ap.parse_args()
    args = Box(args.__dict__)

    return args


def pull_2d_points() -> None:
    return
