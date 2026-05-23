import numpy as np

def sys_nonlinear_terms(x, y, a=0.5, b=0.2):
    """
    Computes the nonlinearities to be negated by the controller.
    e_dot = y_dot - gamma * x_dot.
    So the uncontrolled e_dot is response_field(y, 0) - gamma * drive_field(x).
    We extract the terms corresponding to the system dynamics here.
    Wait, in projective synchronization with gamma, e_i = y_i - gamma_i x_i.
    Actually, let's look at how projective synchronization handles the system nonlinearities.
    The response system is: D^q y = f(y) + u.
    The drive system is: D^q x = f(x).
    So D^q e = f(y) + u - gamma * f(x).
    We want D^q e = ... (sliding surface reaching law).
    So we need u to cancel f(y) - gamma * f(x).
    Therefore, sys_nonlinearities = f(y) - gamma * f(x).
    """
    from chaos.drive_system import drive_field
    from chaos.response_system import response_field
    
    f_y = response_field(y, np.zeros(6), a=a, b=b)
    f_x = drive_field(x, a=a, b=b)
    
    return f_y - f_x # Assumes gamma is array of 1s or handled correctly. If gamma != 1, it's f_y - gamma * f_x.

def compute_nonlinear_cancellation(x, y, gamma, a=0.5, b=0.2):
    from chaos.drive_system import drive_field
    from chaos.response_system import response_field
    f_y = response_field(y, np.zeros(6), a=a, b=b)
    f_x = drive_field(x, a=a, b=b)
    return f_y - gamma * f_x
