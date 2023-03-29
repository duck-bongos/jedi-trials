"""A module to read in an .obj file and write the textures to an image.

	Author: Dan Billmann

"""
import re
import sys

import numpy as np


def add_colors_to_disc(mesh):
    return


def extract(readlist, numeric=False) -> list:
    readlist = [r.split(" ")[1:] for r in readlist]

    if numeric:
        extracted = np.array(readlist).astype(float)

    else:
        extracted = np.array(readlist)

    return extracted


if __name__ in "__main__":
    with open(sys.argv[1], "r") as o:
        obj = o.read()

    with open(sys.argv[2], "r") as ol:
        og = ol.read()

    v_ = re.findall("v\ .*", obj)
    t_ = re.findall("vt\ .*", obj)
    f_ = re.findall("f\ .*", obj)
    og_ = re.findall("v\ .*", og)
    gg = extract(og_, numeric=True)
    vertices = extract(v_, numeric=True)
    textures = extract(t_, numeric=True)
    faces = extract(f_)

    print(type(vertices), type(textures), type(faces))

    # option 1: write all texture lines as vertex lines
