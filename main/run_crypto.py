import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from fractional_core.abm_solver import ABMSolver
from fractional_core.generator import generate_fractional_sequences
from sync.integrator import FractionalIntegrator
from sync.sliding_surface import compute_sigma
from sync.controller import compute_control
from sync.synchronizer import compute_nonlinear_cancellation
from chaos.response_system import response_field
from crypto.key_extractor import extract_keys
from crypto.image_cipher import encrypt_image, decrypt_image
from paper_mode.direct_key_extractor import extract_paper_keys
from paper_mode.direct_encrypt import encrypt_paper
from paper_mode.direct_decrypt import decrypt_paper

def load_image(filepath, target_size=(100, 100)):
    """Loads image, converts to grayscale, resizes to keep simulation time practical."""
    print(f"Loading image from {filepath}...")
    img = Image.open(filepath).convert('L')
    img = img.resize(target_size)
    img_array = np.array(img, dtype=np.uint8)
    return img_array

def run_synchronization(total_steps, x_trajectory):
    """Executes explicit ABM-PC synchronization against a pre-computed drive trajectory."""
    print(f"Initializing Fractional Synchronization for {total_steps} steps...")
    
    response_solver = ABMSolver(q=config.Q, dt=config.DT, truncation_window=config.L)
    
    e_integrator = FractionalIntegrator(q=config.Q, dt=config.DT, truncation_window=config.L)
    e_nu_integrator = FractionalIntegrator(q=config.Q, dt=config.DT, truncation_window=config.L)
    
    y0 = np.array([5.0, -3.0, 2.0, -4.0, 1.0, -2.0], dtype=np.float64)
    x0 = x_trajectory[0]
    
    y_hist = np.zeros((config.L, 6), dtype=np.float64)
    f_y_hist = np.zeros((config.L, 6), dtype=np.float64)
    
    e_hist = np.zeros((config.L, 6), dtype=np.float64)
    e_nu_hist = np.zeros((config.L, 6), dtype=np.float64)
    
    y_trajectory = np.zeros((total_steps, 6), dtype=np.float64)
    errors_trajectory = np.zeros((total_steps, 6), dtype=np.float64)
    
    y_hist[0] = y0
    
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
    
    y_trajectory[0] = y0
    errors_trajectory[0] = e0
    
    n_hist = 1
    synchronized = False
    
    for i in range(1, total_steps):
        valid_f_y = f_y_hist[:n_hist]
        valid_e = e_hist[:n_hist]
        valid_e_nu = e_nu_hist[:n_hist]
        
        # 1. GET PRE-COMPUTED DRIVE STATE
        x_next = x_trajectory[i]
        x_pred = x_trajectory[i] # Approximated for nonlinear cancellation
        
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
        
        y_trajectory[i] = y_next
        errors_trajectory[i] = y_next - config.GAMMA * x_next
        
        if n_hist < config.L:
            y_hist[n_hist] = y_next
            f_y_hist[n_hist] = f_y_next
            e_hist[n_hist] = errors_trajectory[i]
            e_nu_hist[n_hist] = e_nu_next
            n_hist += 1
        else:
            y_hist[:-1] = y_hist[1:]
            y_hist[-1] = y_next
            f_y_hist[:-1] = f_y_hist[1:]
            f_y_hist[-1] = f_y_next
            e_hist[:-1] = e_hist[1:]
            e_hist[-1] = errors_trajectory[i]
            e_nu_hist[:-1] = e_nu_hist[1:]
            e_nu_hist[-1] = e_nu_next
            
        if not synchronized and i > config.DISCARD_STEPS:
            if np.max(np.abs(errors_trajectory[i])) < config.SYNC_THRESHOLD:
                synchronized = True
                print(f"[*] Synchronization lock achieved at step {i}!")
                
        if i % 2000 == 0:
            err_norm = np.linalg.norm(errors_trajectory[i])
            print(f"Simulation Step {i}/{total_steps} | Error: {err_norm:.2e}")
            
    if not synchronized:
        print("[!] WARNING: Strict synchronization threshold not met.")
    
    return y_trajectory

def save_image(img_array, shape, filename):
    img = Image.fromarray(img_array.reshape(shape), mode='L')
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'results', filename)
    img.save(path)
    print(f"Saved {path}")
    return path

def main():
    print("=== Fractional-Order Hyperchaotic Secure Communication Demo ===")
    
    # 1. LOAD IMAGE
    image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'images', 'test.png')
    img_array = load_image(image_path, target_size=(100, 100))
    img_shape = img_array.shape
    img_bytes = img_array.flatten()
    N = len(img_bytes)
    print(f"Image loaded: {img_shape} -> {N} bytes.")
    
    # Calculate required steps to get enough chaotic keys
    total_steps = config.DISCARD_STEPS + N
    
    # 2. GENERATE DRIVE SEQUENCES (Decoupled Transmitter)
    print(f"Generating Transmitting Drive Sequences for {total_steps} steps...")
    x_traj = generate_fractional_sequences(total_steps, discard_transients=False)
    
    # 3. RUN SYNCHRONIZATION (Receiver)
    y_traj = run_synchronization(total_steps, x_traj)
    
    # Ensure we only use states after transients
    x_sync = x_traj[config.DISCARD_STEPS : config.DISCARD_STEPS + N]
    y_sync = y_traj[config.DISCARD_STEPS : config.DISCARD_STEPS + N]
    
    # 4. EXTRACT CHAOTIC KEYS
    if getattr(config, 'MODE', 'robust') == 'paper':
        print("[*] Running in PAPER mode (Direct Quantization, no PRNG/SHA-256)")
        tx_keys = extract_paper_keys(x_sync)
        rx_keys = extract_paper_keys(y_sync)
    else:
        print("[*] Running in ROBUST mode (SHA-256 seed + PRNG expansion)")
        tx_keys = extract_keys(x_sync)
        rx_keys = extract_keys(y_sync)
    
    # Verify that independent key generation results in identical keys
    keys_match = np.array_equal(tx_keys, rx_keys)
    print(f"[*] Checking key parity between transmitter and receiver: {'MATCHED' if keys_match else 'FAILED'}")
    assert keys_match, "CRITICAL ERROR: Key mismatch between transmitter and receiver!"
    
    # 5. ENCRYPTION (Transmitter side)
    print("Encrypting image...")
    if getattr(config, 'MODE', 'robust') == 'paper':
        encrypted_bytes = encrypt_paper(img_bytes, x_sync)
    else:
        encrypted_bytes = encrypt_image(img_bytes, tx_keys)
    save_image(encrypted_bytes, img_shape, 'encrypted.png')
    
    # 6. DECRYPTION (Receiver side)
    print("Decrypting image...")
    if getattr(config, 'MODE', 'robust') == 'paper':
        decrypted_bytes = decrypt_paper(encrypted_bytes, y_sync)
    else:
        decrypted_bytes = decrypt_image(encrypted_bytes, rx_keys)
    save_image(decrypted_bytes, img_shape, 'decrypted.png')
    
    # 7. VALIDATION
    match = np.array_equal(img_bytes, decrypted_bytes)
    print("\n=== Validation Results ===")
    print(f"Total Pixels: {N}")
    print(f"Decryption Match: {'SUCCESS' if match else 'FAILED'}")
    
    # 8. SAVE COMPARISON PLOT
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 3, 1)
    plt.title("Original", fontsize=14)
    plt.imshow(img_array, cmap='gray')
    plt.axis('off')
    
    plt.subplot(1, 3, 2)
    plt.title("Encrypted", fontsize=14)
    plt.imshow(encrypted_bytes.reshape(img_shape), cmap='gray')
    plt.axis('off')
    
    plt.subplot(1, 3, 3)
    plt.title("Decrypted", fontsize=14)
    plt.imshow(decrypted_bytes.reshape(img_shape), cmap='gray')
    plt.axis('off')
    
    comp_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'results', 'comparison.png')
    plt.savefig(comp_path, dpi=300, bbox_inches='tight')
    print(f"Saved side-by-side comparison to {comp_path}")
    print("===============================================================")

if __name__ == "__main__":
    main()
