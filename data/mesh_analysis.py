import pymeshlab
import numpy as np

MS = pymeshlab.MeshSet()

fpath = "mapped/source.obj"

MS.load_new_mesh(fpath)

m = MS.current_mesh().vertex_matrix()
q = "(vi==8829)"
MS.compute_selection_by_condition_per_vertex(condselect=q)

print()
