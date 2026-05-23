import numpy as np

def drive_field(x, a=0.5, b=0.2):
    """
    Computes the vector field of the 6D hyperchaotic drive system.
    Equation (3.2) from the paper.
    """
    x1, x2, x3, x4, x5, x6 = x

    dx1 = a * (-x1 + x2) + x4
    dx2 = -x3 * np.sign(x1)
    dx3 = -1 + np.abs(x1)
    dx4 = -b * np.cos(x2)
    dx5 = -x5 + x1 * x4
    dx6 = -x6 + x1 * x3

    return np.array([dx1, dx2, dx3, dx4, dx5, dx6])
