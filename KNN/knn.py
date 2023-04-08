import sys
import math
import numpy as np
from sklearn.neighbors import KDTree


def read_point_cloud(filename):
    points = []
    with open(filename, "r") as f:
        for line in f:
            if line.startswith("v "):
                parts = line.split()
                x, y, z = map(float, parts[1:])
                points.append([x, y])
    return np.array(points)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python knn.py <source.obj> <target.obj>")
        sys.exit(1)

    # Read the source and target point clouds.
    source_points = read_point_cloud(sys.argv[1])
    target_points = read_point_cloud(sys.argv[2])

    # Build KD Tree for target point cloud.
    tree = KDTree(target_points)

    # Perform K-Nearest Neighbors between the source and target point clouds.
    k = 1  # set k to 1 for nearest neighbor search
    distances, indices = tree.query(source_points, k=k)
    for i, index in enumerate(indices):
        print(f"Vertex {i} in source cloud maps to vertex {index} in target cloud")
