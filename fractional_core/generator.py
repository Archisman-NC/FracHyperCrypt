import sys
import os
import numpy as np

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from fractional_core.abm_solver import ABMSolver
from chaos.drive_system import drive_field

def generate_fractional_sequences(length, discard_transients=True):
    """
    Generates chaotic sequences using the mathematically corrected fractional-order 
    Adams-Bashforth-Moulton predictor-corrector numerical method.
    
    Args:
        length (int): The number of chaotic state vectors to generate.
        discard_transients (bool): If True, discards config.DISCARD_STEPS initial steps
                                   to ensure trajectories are fully on the chaotic attractor.
                                   
    Returns:
        np.ndarray: Array of shape (length, 6) containing the fractional chaotic states.
    """
    # Total steps to compute
    transient_steps = config.DISCARD_STEPS if discard_transients else 0
    total_steps = transient_steps + length
    
    # Initialize the mathematically corrected ABM solver
    solver = ABMSolver(q=config.Q, dt=config.DT, truncation_window=config.L, dim=6)
    
    # Initial conditions
    x0 = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0], dtype=np.float64)
    
    # Pre-allocate history buffers for sliding window (Short Memory Principle)
    f_history = np.zeros((config.L, 6), dtype=np.float64)
    f_history[0] = drive_field(x0, a=config.A, b=config.B)
    
    # Pre-allocate trajectory memory. For large lengths, we only store what we need.
    trajectory = np.zeros((length, 6), dtype=np.float64)
    
    if not discard_transients and length > 0:
        trajectory[0] = x0
        
    n_hist = 1
    
    for i in range(1, total_steps):
        valid_f_hist = f_history[:n_hist]
        
        # 1. Fractional Predictor Step (Adams-Bashforth)
        x_pred = solver.predict(x0, valid_f_hist)
        f_pred = drive_field(x_pred, a=config.A, b=config.B)
        
        # 2. Fractional Corrector Step (Adams-Moulton)
        x_next = solver.correct(x0, valid_f_hist, f_pred)
        f_next = drive_field(x_next, a=config.A, b=config.B)
        
        # Store in output trajectory if past transient phase
        if i >= transient_steps:
            idx = i - transient_steps
            trajectory[idx] = x_next
            
        # Update sliding history buffer
        if n_hist < config.L:
            f_history[n_hist] = f_next
            n_hist += 1
        else:
            f_history[:-1] = f_history[1:]
            f_history[-1] = f_next
            
    return trajectory
