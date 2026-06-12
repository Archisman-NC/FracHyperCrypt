import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from fractional_core.abm_solver import ABMSolver
from sync.integrator import FractionalIntegrator
from sync.sliding_surface import compute_sigma
from sync.controller import compute_control
from sync.synchronizer import compute_nonlinear_cancellation
from chaos.drive_system import drive_field
from chaos.response_system import response_field

def main():
    print("Initializing Fractional Synchronization Engine...")
    
    # Solvers
    drive_solver = ABMSolver(q=config.Q, dt=config.DT, truncation_window=config.L)
    response_solver = ABMSolver(q=config.Q, dt=config.DT, truncation_window=config.L)
    
    # Fractional Integrators for sliding surface memory
    e_integrator = FractionalIntegrator(q=config.Q, dt=config.DT, truncation_window=config.L)
    e_nu_integrator = FractionalIntegrator(q=config.Q, dt=config.DT, truncation_window=config.L)
    
    # Initial conditions
    x0 = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0], dtype=np.float64)
    y0 = np.array([5.0, -3.0, 2.0, -4.0, 1.0, -2.0], dtype=np.float64)
    
    # History buffers for state and vector field
    x_hist = np.zeros((config.L, 6), dtype=np.float64)
    f_x_hist = np.zeros((config.L, 6), dtype=np.float64)
    
    y_hist = np.zeros((config.L, 6), dtype=np.float64)
    f_y_hist = np.zeros((config.L, 6), dtype=np.float64)
    
    # History buffers for error terms needed by integrators
    e_hist = np.zeros((config.L, 6), dtype=np.float64)
    e_nu_hist = np.zeros((config.L, 6), dtype=np.float64)
    
    # Tracking for plotting
    errors_trajectory = np.zeros((config.STEPS, 6), dtype=np.float64)
    sigma_trajectory = np.zeros((config.STEPS, 6), dtype=np.float64)
    u_trajectory = np.zeros((config.STEPS, 6), dtype=np.float64)
    
    # Initialize buffers
    x_hist[0] = x0
    y_hist[0] = y0
    f_x_hist[0] = drive_field(x0, a=config.A, b=config.B)
    
    e0 = y0 - config.GAMMA * x0
    e_hist[0] = e0
    e_nu_hist[0] = e0 * np.power(e0**2 + config.EPSILON, config.NU / 2.0)
    
    # Controller requires initial sigma
    I_e0 = e_integrator.integrate(e_hist[:1])
    I_e_nu0 = e_nu_integrator.integrate(e_nu_hist[:1])
    sigma0 = compute_sigma(e0, I_e0, I_e_nu0, alpha=config.ALPHA, beta=config.BETA)
    
    u0 = compute_control(e0, sigma0, compute_nonlinear_cancellation(x0, y0, config.GAMMA, a=config.A, b=config.B), 
                         alpha=config.ALPHA, beta=config.BETA, theta=config.THETA, delta=config.DELTA, 
                         nu=config.NU, mu=config.MU, epsilon=config.EPSILON, clip_limit=config.CLIP_LIMIT)
    f_y_hist[0] = response_field(y0, u0, a=config.A, b=config.B)
    
    errors_trajectory[0] = e0
    sigma_trajectory[0] = sigma0
    u_trajectory[0] = u0
    
    n_hist = 1
    synchronized = False
    
    print(f"Running {config.STEPS} synchronization steps...")
    
    for i in range(1, config.STEPS):
        # Current valid history
        valid_f_x = f_x_hist[:n_hist]
        valid_f_y = f_y_hist[:n_hist]
        valid_e = e_hist[:n_hist]
        valid_e_nu = e_nu_hist[:n_hist]
        
        # --- 1. DRIVE SYSTEM ---
        x_pred = drive_solver.predict(x0, valid_f_x)
        f_x_pred = drive_field(x_pred, a=config.A, b=config.B)
        x_next = drive_solver.correct(x0, valid_f_x, f_x_pred)
        f_x_next = drive_field(x_next, a=config.A, b=config.B)
        
        # --- 2. RESPONSE SYSTEM PREDICTOR ---
        y_pred = response_solver.predict(y0, valid_f_y)
        
        # --- 3. ERROR COMPUTATION ---
        e_next = y_pred - config.GAMMA * x_next # use predicted response for controller
        
        # --- 4. SLIDING SURFACE ---
        e_nu_next = e_next * np.power(e_next**2 + config.EPSILON, config.NU / 2.0)
        
        # Append temporarily to get next integral
        temp_e = np.vstack([valid_e, e_next])[-config.L:]
        temp_e_nu = np.vstack([valid_e_nu, e_nu_next])[-config.L:]
        
        I_e_next = e_integrator.integrate(temp_e)
        I_e_nu_next = e_nu_integrator.integrate(temp_e_nu)
        
        sigma_next = compute_sigma(e_next, I_e_next, I_e_nu_next, alpha=config.ALPHA, beta=config.BETA)
        
        # --- 5. CONTROLLER ---
        sys_nonlin = compute_nonlinear_cancellation(x_next, y_pred, config.GAMMA, a=config.A, b=config.B)
        u_next = compute_control(e_next, sigma_next, sys_nonlin, 
                                 alpha=config.ALPHA, beta=config.BETA, theta=config.THETA, delta=config.DELTA, 
                                 nu=config.NU, mu=config.MU, epsilon=config.EPSILON, clip_limit=config.CLIP_LIMIT)
        
        # --- 6. RESPONSE SYSTEM CORRECTOR ---
        f_y_pred = response_field(y_pred, u_next, a=config.A, b=config.B)
        y_next = response_solver.correct(y0, valid_f_y, f_y_pred)
        f_y_next = response_field(y_next, u_next, a=config.A, b=config.B)
        
        # Save metrics
        errors_trajectory[i] = y_next - config.GAMMA * x_next
        sigma_trajectory[i] = sigma_next
        u_trajectory[i] = u_next
        
        # Update sliding window buffers
        if n_hist < config.L:
            x_hist[n_hist] = x_next
            f_x_hist[n_hist] = f_x_next
            y_hist[n_hist] = y_next
            f_y_hist[n_hist] = f_y_next
            e_hist[n_hist] = errors_trajectory[i]
            e_nu_hist[n_hist] = e_nu_next
            n_hist += 1
        else:
            x_hist[:-1] = x_hist[1:]
            x_hist[-1] = x_next
            f_x_hist[:-1] = f_x_hist[1:]
            f_x_hist[-1] = f_x_next
            
            y_hist[:-1] = y_hist[1:]
            y_hist[-1] = y_next
            f_y_hist[:-1] = f_y_hist[1:]
            f_y_hist[-1] = f_y_next
            
            e_hist[:-1] = e_hist[1:]
            e_hist[-1] = errors_trajectory[i]
            e_nu_hist[:-1] = e_nu_hist[1:]
            e_nu_hist[-1] = e_nu_next
            
        # Lock detection
        if not synchronized and i > config.DISCARD_STEPS:
            if np.max(np.abs(errors_trajectory[i])) < config.SYNC_THRESHOLD:
                synchronized = True
                print(f"[*] Synchronization lock detected at step {i}!")
                
        if i % 1000 == 0:
            err_norm = np.linalg.norm(errors_trajectory[i])
            print(f"Step {i}/{config.STEPS} | Error L2: {err_norm:.2e} | Control Max: {np.max(np.abs(u_next)):.2f}")

    print("Synchronization simulation complete. Plotting...")
    
    # Plot errors
    plt.figure(figsize=(10, 6))
    for dim in range(6):
        plt.plot(errors_trajectory[:, dim], label=f'e_{dim+1}', lw=1)
    plt.title('Projective Synchronization Errors e_i(t)')
    plt.xlabel('Steps')
    plt.ylabel('Error')
    plt.yscale('symlog', linthresh=1e-8)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'results', 'sync_errors.png')
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved {output_path}")

if __name__ == "__main__":
    main()

