import cv2
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Polygon

path = "../../data/source/source.png"
contour = [
    (109, 10),
    (10, 338),
    (338, 297),
    (297, 332),
    (332, 284),
    (284, 251),
    (251, 389),
    (389, 356),
    (356, 454),
    (454, 323),
    (323, 361),
    (361, 288),
    (288, 397),
    (397, 365),
    (365, 379),
    (379, 378),
    (378, 400),
    (400, 377),
    (377, 152),
    (152, 148),
    (148, 176),
    (176, 149),
    (149, 150),
    (150, 136),
    (136, 172),
    (172, 58),
    (58, 132),
    (132, 93),
    (93, 234),
    (234, 127),
    (127, 162),
    (162, 21),
    (21, 54),
    (54, 103),
    (103, 67),
    (67, 109),
]

polygon = Polygon(contour)

plt.plot(*polygon.exterior.xy)
plt.show()

# int_coords = lambda x: np.array(x).round().astype(np.int32)
# exterior = [int_coords(polygon.exterior.coords)]

# alpha = 0.1  # that's your transparency factor


# image = cv2.imread(path)
# overlay = image.copy()
# cv2.fillPoly(overlay, exterior, color=(255, 255, 0))
# cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)
# cv2.imshow("Polygon", image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
