import numpy as np
from cmath import sqrt


def mobius_transform(z1, z2, z3, w1, w2, w3):
    c1 = (w2 - w3) * (z1 - z3) - (w1 - w3) * (z2 - z3)
    c2 = (w2 - w3) * (z1 * z1 - z3 * z3) - (w1 - w3) * (z2 * z2 - z3 * z3)
    c3 = (w1 - w3) * (z2 - z3) - (w2 - w3) * (z1 - z3)
    c4 = (w1 - w3) * (z2 * z3 - z3 * z2) - (w2 - w3) * (z1 * z3 - z3 * z1)

    def f(z):
        numerator = c1 * z + c2
        denominator = c3 * z + c4
        return (numerator / denominator - w3) / (w2 - w3) * (z - z3) + w3

    return f


z1 = 0.781325 + 0.390844j  # left_eye
z2 = 0.818426 + 0.328055j  # right_eye
z3 = 0.650057 + 0.456952j  # nosetip

w1 = complex(-0.5, 1) / (2 * sqrt(2))
w2 = complex(+0.5, 1) / (2 * sqrt(2))
w3 = complex(0, 0)

f = mobius_transform(z1, z2, z3, w1, w2, w3)

print(f"nosetip': {f(z3)}\t{w3}\nleft eye': {f(z1)}\t{w1}\nright eye': {f(z2)}\t{w2}")
