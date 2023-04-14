# Data


### Directory
 - boundary: Output from `../boundary_detection`. `.obj` files with a trimmed boundary.
 - collapsed: Output from `../quadric_edge_collapse_decimation`. Significantly reduced # of faces and vertices
 - keypoints: Files containing vertex indices of the selected points in `../boundary_detection/mediapipe_constants/keypoint_idx.txt`. Gets updated when running QECD.
 - mapped: Output from `../HarmonicMap` with the `.obj` discs in $\mathbb{R}^2$.
 - metrics: Similar to `./keypoints` except with points for evalutating metrics. Also containts distance calculations in `./metrics/metrics.txt`.
 - registration: Output from `../non_rigid_registration`. Contains a map of vertex indices in the form `<source_id1> <target_id1>\n<source_id2> <target_id2>`.
 - transformed: Output from `../mobius`. Contains the Möbius transformed $\mathbb{R}^2$ discs.
 - source.obj: Default input source object.
 - source.png: Default input source image.
 - target.obj: Default input target object.
 - target.obj: Default input target image.
 - <source_texture.txt>: Texture values from the source object. Generated from `../boundary_detection`.
 - <source_voxels.txt>: Voxel values from the source object. Generated from `../boundary_detection`.
 - <target_texture.txt>: Texture values from the target object. Generated from `../boundary_detection`.
 - <target_voxels.txt>: Voxel values from the target object. Generated from `../boundary_detection`.

#### NOTE: Named Files
Each directory has a file by the same name (`metrics/metrics`) to ensure the directory is added to git.