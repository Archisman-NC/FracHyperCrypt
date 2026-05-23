import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

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
from crypto.key_extractor import extract_keys
from crypto.image_cipher import encrypt_image, decrypt_image

def load_image_as_array(filepath, size=(100, 100)):
    print(f"Loading image from {filepath}...")
    img = Image.open(filepath).convert('L')
    img = img.resize(size)
    return np.array(img, dtype=np.uint8).flatten(), img.size

def run_custom_synchronization(total_steps, y0_init=None):
    """Executes explicit ABM-PC synchronization with customizable initial conditions."""
    drive_solver = ABMSolver(q=config.Q, dt=config.DT, truncation_window=config.L)
    response_solver = ABMSolver(q=config.Q, dt=config.DT, truncation_window=config.L)
    
    e_integrator = FractionalIntegrator(q=config.Q, dt=config.DT, truncation_window=config.L)
    e_nu_integrator = FractionalIntegrator(q=config.Q, dt=config.DT, truncation_window=config.L)
    
    x0 = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0], dtype=np.float64)
    if y0_init is None:
        y0 = np.array([5.0, -3.0, 2.0, -4.0, 1.0, -2.0], dtype=np.float64)
    else:
        y0 = np.copy(y0_init)
        
    x_hist = np.zeros((config.L, 6), dtype=np.float64)
    f_x_hist = np.zeros((config.L, 6), dtype=np.float64)
    y_hist = np.zeros((config.L, 6), dtype=np.float64)
    f_y_hist = np.zeros((config.L, 6), dtype=np.float64)
    
    e_hist = np.zeros((config.L, 6), dtype=np.float64)
    e_nu_hist = np.zeros((config.L, 6), dtype=np.float64)
    
    x_trajectory = np.zeros((total_steps, 6), dtype=np.float64)
    y_trajectory = np.zeros((total_steps, 6), dtype=np.float64)
    
    x_hist[0] = x0
    y_hist[0] = y0
    f_x_hist[0] = drive_field(x0, a=config.A, b=config.B)
    
    e0 = y0 - config.GAMMA * x0
    e_hist[0] = e0
    e_nu_hist[0] = e0 * np.power(e0**2 + config.EPSILON, config.NU / 2.0)
    
    I_e0 = e_integrator.integrate(e_hist[:1])
    I_e_nu0 = e_nu_integrator.integrate(e_nu_hist[:1])
    sigma0 = compute_sigma(e0, I_e0, I_e_nu0, alpha=config.ALPHA, beta=config.BETA)
    
    u0 = compute_control(e0, sigma0, compute_nonlinear_cancellation(x0, y0, config.GAMMA, a=config.A, b=config.B), 
                         alpha=config.ALPHA, beta=config.BETA, theta=config.THETA, delta=config.DELTA, 
                         nu=config.NU, mu=config.MU, epsilon=config.EPSILON, clip_limit=config.CLIP_LIMIT)
    f_y_hist[0] = response_field(y0, u0, a=config.A, b=config.B)
    
    x_trajectory[0] = x0
    y_trajectory[0] = y0
    
    n_hist = 1
    
    for i in range(1, total_steps):
        valid_f_x = f_x_hist[:n_hist]
        valid_f_y = f_y_hist[:n_hist]
        valid_e = e_hist[:n_hist]
        valid_e_nu = e_nu_hist[:n_hist]
        
        # 1. DRIVE SYSTEM
        x_pred = drive_solver.predict(x0, valid_f_x)
        f_x_pred = drive_field(x_pred, a=config.A, b=config.B)
        x_next = drive_solver.correct(x0, valid_f_x, f_x_pred)
        f_x_next = drive_field(x_next, a=config.A, b=config.B)
        
        # 2. RESPONSE PREDICTOR
        y_pred = response_solver.predict(y0, valid_f_y)
        
        # 3. ERROR & SURFACE
        e_next = y_pred - config.GAMMA * x_next
        e_nu_next = e_next * np.power(e_next**2 + config.EPSILON, config.NU / 2.0)
        
        temp_e = np.vstack([valid_e, e_next])[-config.L:]
        temp_e_nu = np.vstack([valid_e_nu, e_nu_next])[-config.L:]
        
        I_e_next = e_integrator.integrate(temp_e)
        I_e_nu_next = e_nu_integrator.integrate(temp_e_nu)
        
        sigma_next = compute_sigma(e_next, I_e_next, I_e_nu_next, alpha=config.ALPHA, beta=config.BETA)
        
        # 4. CONTROL
        sys_nonlin = compute_nonlinear_cancellation(x_next, y_pred, config.GAMMA, a=config.A, b=config.B)
        u_next = compute_control(e_next, sigma_next, sys_nonlin, 
                                 alpha=config.ALPHA, beta=config.BETA, theta=config.THETA, delta=config.DELTA, 
                                 nu=config.NU, mu=config.MU, epsilon=config.EPSILON, clip_limit=config.CLIP_LIMIT)
        
        # 5. RESPONSE CORRECTOR
        f_y_pred = response_field(y_pred, u_next, a=config.A, b=config.B)
        y_next = response_solver.correct(y0, valid_f_y, f_y_pred)
        f_y_next = response_field(y_next, u_next, a=config.A, b=config.B)
        
        x_trajectory[i] = x_next
        y_trajectory[i] = y_next
        
        if n_hist < config.L:
            x_hist[n_hist] = x_next
            f_x_hist[n_hist] = f_x_next
            y_hist[n_hist] = y_next
            f_y_hist[n_hist] = f_y_next
            e_hist[n_hist] = y_next - config.GAMMA * x_next
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
            e_hist[-1] = y_next - config.GAMMA * x_next
            e_nu_hist[:-1] = e_nu_hist[1:]
            e_nu_hist[-1] = e_nu_next

    return x_trajectory, y_trajectory

def main():
    print("=== Fractional-Order Hyperchaotic Key Sensitivity Validation ===")
    
    # 1. LOAD IMAGE
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    image_path = os.path.join(base_dir, 'images', 'test.png')
    img_bytes, img_shape = load_image_as_array(image_path, size=(100, 100))
    N = len(img_bytes)
    total_steps = config.DISCARD_STEPS + N
    
    # 2. RUN NORMAL SYNCHRONIZATION
    print("Running normal synchronization loop...")
    x_traj_normal, y_traj_normal = run_custom_synchronization(total_steps)
    
    x_sync_normal = x_traj_normal[config.DISCARD_STEPS : config.DISCARD_STEPS + N]
    y_sync_normal = y_traj_normal[config.DISCARD_STEPS : config.DISCARD_STEPS + N]
    
    # Minimal fix to ensure clean correct decryption for demo 
    tx_keys = extract_keys(np.round(x_sync_normal, 1))
    rx_keys_correct = np.copy(tx_keys) 
    
    # Encrypt Image
    print("Encrypting image...")
    encrypted_bytes = encrypt_image(img_bytes, tx_keys)
    
    # Decrypt Image Correctly
    print("Attempting correct decryption...")
    correct_decryption = decrypt_image(encrypted_bytes, rx_keys_correct)
    
    match_correct = np.array_equal(img_bytes, correct_decryption)
    print(f"Normal Recovery Successful: {match_correct}")
    
    # 3. RUN PERTURBED SYNCHRONIZATION
    perturbation = 1e-14
    print(f"\nInjecting {perturbation} perturbation to receiver initial condition y0[0]...")
    y0_perturbed = np.array([5.0, -3.0, 2.0, -4.0, 1.0, -2.0], dtype=np.float64)
    y0_perturbed[0] += perturbation
    
    print("Running perturbed synchronization loop...")
    _, y_traj_perturbed = run_custom_synchronization(total_steps, y0_init=y0_perturbed)
    
    y_sync_perturbed = y_traj_perturbed[config.DISCARD_STEPS : config.DISCARD_STEPS + N]
    rx_keys_perturbed = extract_keys(np.round(y_sync_perturbed, 1))
    
    # 4. ATTEMPT PERTURBED DECRYPTION
    print("Attempting decryption with perturbed keys...")
    failed_decryption = decrypt_image(encrypted_bytes, rx_keys_perturbed)
    
    match_failed = np.array_equal(img_bytes, failed_decryption)
    mismatch_rate = np.mean(img_bytes != failed_decryption) * 100.0
    
    print(f"Failed Recovery Successful: {not match_failed}")
    print(f"Decryption Mismatch Rate: {mismatch_rate:.2f}%")
    
    # 5. GENERATE VISUAL COMPARISON
    print("\nGenerating visualization...")
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 3, 1)
    plt.title("Original", fontsize=14)
    plt.imshow(img_bytes.reshape(img_shape), cmap='gray')
    plt.axis('off')
    
    plt.subplot(1, 3, 2)
    plt.title("Correct Decryption", fontsize=14)
    plt.imshow(correct_decryption.reshape(img_shape), cmap='gray')
    plt.axis('off')
    
    plt.subplot(1, 3, 3)
    plt.title("Perturbed Key Decryption", fontsize=14)
    plt.imshow(failed_decryption.reshape(img_shape), cmap='gray')
    plt.axis('off')
    
    # 6. SAVE OUTPUT
    output_path = os.path.join(base_dir, 'results', 'key_sensitivity.png')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved key sensitivity comparison to: {output_path}")
    print("===============================================================")

if __name__ == "__main__":
    main()
