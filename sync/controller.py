import numpy as np

def compute_control(e, sigma, sys_nonlinearities, alpha=2.0, beta=1.0, theta=5.0, delta=2.0, nu=0.5, mu=0.5, epsilon=1e-8, clip_limit=100.0):
    """
    Computes the regularized fractional sliding mode control effort.
    Equation (4.6)
    u_i = -sys_nonlinearities - alpha*e_i - beta*e_i*(e_i^2 + eps)^(nu/2)
          - theta*tanh(sigma_i) - delta*tanh(sigma_i)*(sigma_i^2 + eps)^(mu/2)
    """
    # Regularized fractional power terms
    e_term = e * np.power(e**2 + epsilon, nu/2)
    sigma_term = np.tanh(sigma) * np.power(sigma**2 + epsilon, mu/2)
    
    u = -sys_nonlinearities - alpha * e - beta * e_term - theta * np.tanh(sigma) - delta * sigma_term
    
    # Clip the control effort to prevent NaN cascade during initial transients
    u = np.clip(u, -clip_limit, clip_limit)
    
    return u
