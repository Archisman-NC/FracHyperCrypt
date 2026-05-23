import numpy as np

def response_field(y, u, a=0.5, b=0.2):
    """
    Computes the vector field of the 6D hyperchaotic response system.
    Equation (3.3) from the paper.
    u is the control input vector.
    """
    y1, y2, y3, y4, y5, y6 = y
    u1, u2, u3, u4, u5, u6 = u

    dy1 = a * (-y1 + y2) + y4 + u1
    dy2 = -y3 * np.sign(y1) + u2
    dy3 = -1 + np.abs(y1) + u3
    dy4 = -b * np.cos(y2) + u4
    dy5 = -y5 + y1 * y4 + u5
    dy6 = -y6 + y1 * y3 + u6

    return np.array([dy1, dy2, dy3, dy4, dy5, dy6])
