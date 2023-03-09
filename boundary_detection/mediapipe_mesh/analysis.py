import matplotlib.pyplot as plt
import numpy as np
from pywavefront import Wavefront

fpath = "C:\\Users\\dan\\Documents\\GitHub\\jedi-trials\\data\\source\\source.obj"

scene = Wavefront(fpath, create_materials=True)

print(scene.vertices)

