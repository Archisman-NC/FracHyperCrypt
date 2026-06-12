import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from fractional_core.abm_solver import ABMSolver
from chaos.drive_system import drive_field

def main():
    print("Initializing Fractional ABM-PC Solver...")
    
    solver = ABMSolver(q=config.Q, dt=config.DT, truncation_window=config.L)
    
    # History buffer for x states and f(x) evaluations
    x_history = np.zeros((config.L, 6), dtype=np.float64)
    f_history = np.zeros((config.L, 6), dtype=np.float64)
    
    # Initial condition
    x0 = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0], dtype=np.float64)
    
    # Setup history buffers properly
    x_history[0] = x0
    f_history[0] = drive_field(x0)
    
    # We will store the full trajectory for plotting
    trajectory = np.zeros((config.STEPS, 6), dtype=np.float64)
    trajectory[0] = x0
    
    # Length of populated history
    n_hist = 1
    
    print(f"Simulating {config.STEPS} steps (dt={config.DT}, q={config.Q}, L={config.L})...")
    
    for i in range(1, config.STEPS):
        # Current state
        x_curr = trajectory[i-1]
        
        # Determine the slice of valid history
        valid_f_hist = f_history[:n_hist]
        
        # 1. Predictor step
        x_pred = solver.predict(x0, valid_f_hist)
        f_pred = drive_field(x_pred)
        
        # 2. Corrector step
        x_next = solver.correct(x0, valid_f_hist, f_pred)
        f_next = drive_field(x_next)
        
        # 3. Save and update history
        trajectory[i] = x_next
        
        # Update history buffer (sliding window)
        if n_hist < config.L:
            x_history[n_hist] = x_next
            f_history[n_hist] = f_next
            n_hist += 1
        else:
            # Shift left and append at the end
            x_history[:-1] = x_history[1:]
            f_history[:-1] = f_history[1:]
            x_history[-1] = x_next
            f_history[-1] = f_next
            
        if i % 1000 == 0:
            print(f"Step {i}/{config.STEPS} | Max state val: {np.max(np.abs(x_next)):.2f}")
            
    print("Simulation complete. Plotting attractors...")
    
    # Plot phase portraits (discard first DISCARD_STEPS steps as transient)
    transient = config.DISCARD_STEPS
    if transient >= config.STEPS:
        transient = config.STEPS // 2
        
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    axes[0].plot(trajectory[transient:, 0], trajectory[transient:, 1], lw=0.5, alpha=0.8)
    axes[0].set_title('x1-x2 phase portrait')
    axes[0].set_xlabel('x1')
    axes[0].set_ylabel('x2')
    
    axes[1].plot(trajectory[transient:, 1], trajectory[transient:, 2], lw=0.5, alpha=0.8)
    axes[1].set_title('x2-x3 phase portrait')
    axes[1].set_xlabel('x2')
    axes[1].set_ylabel('x3')
    
    axes[2].plot(trajectory[transient:, 0], trajectory[transient:, 3], lw=0.5, alpha=0.8)
    axes[2].set_title('x1-x4 phase portrait')
    axes[2].set_xlabel('x1')
    axes[2].set_ylabel('x4')
    
    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'results', 'attractor.png')
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved {output_path}")

if __name__ == "__main__":
    main()

