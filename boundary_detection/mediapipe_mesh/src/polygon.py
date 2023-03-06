from typing import List, Union

import numpy as np
from shapely import Polygon

class SinglePoly(Polygon):
    def __new__(cls):
        if hasattr("instance", cls):
            cls.instance = super()

    def __init__(self, shell, holes):
        """
        
        Parameters
        ----------
        shell : sequence
            A sequence of (x, y [,z]) numeric coordinate pairs or triples, or
            an array-like with shape (N, 2) or (N, 3).
            Also can be a sequence of Point objects.
        holes : sequence
            A sequence of objects which satisfy the same requirements as the
            shell parameters above
        """
        super().__init__(shell, holes)
    
def create_2d_polygon_boundary(landmarks: np.ndarray) -> Polygon:
    # ensure the points only have 2 dimensions:
    landmarks[:, [0, 1]] = landmarks[:, [1, 0]]

    return Polygon(landmarks)

