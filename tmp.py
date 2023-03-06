"""Figure out how to convert the pixels to the geometric coordinates."""

import numpy as np

obj = np.loadtxt(
    "new.obj",
    delimiter=" ",
)

# rows
print(obj[:, 0].min(), obj[:, 0].max())

# columns
print(obj[:, 1].min(), obj[:, 1].max())

# depth
print(obj[:, 2].min(), obj[:, 2].max())
print()
