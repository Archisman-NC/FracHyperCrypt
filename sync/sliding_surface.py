import numpy as np

def compute_sigma(e_curr, I_e, I_e_nu, alpha=2.0, beta=1.0):
    """
    Computes the fractional sliding surface:
    sigma_i = e_i + alpha * I^q(e_i) + beta * I^q(e_i * |e_i|^nu)
    """
    sigma = e_curr + alpha * I_e + beta * I_e_nu
    return sigma
