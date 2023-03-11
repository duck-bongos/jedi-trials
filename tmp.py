"""Grab the faces"""
import re

with open(
    "/Users/dan/Dropbox/SBU/spring_2023/thesis/jedi-trials/data/annotated/working_objects/source.obj"
) as so:
    s = so.read()
    x = re.findall("f.*", s)
    f = lambda a: set(int(i) for i in re.split("f| |/", a[2:]))
    y = list(map(f, x))
    print(y[0])
    print()
