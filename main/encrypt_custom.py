import sys
import os
import argparse
import time
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
from analysis.entropy import calculate_entropy
from analysis.correlation import get_adjacent_pairs

def load_image(filepath, target_size=(256, 256)):
    """Loads image, converts to grayscale, resizes to target size."""
    if not os.path.exists(filepath):
        print(f"\n[!] ERROR: File not found at '{filepath}'")
        sys.exit(1)
        
    print(f"[*] Loading image from '{filepath}'...")
    img = Image.open(filepath).convert('L')
    img = img.resize(target_size)
    img_array = np.array(img, dtype=np.uint8)
    return img_array

def run_synchronization(total_steps, x_trajectory):
    """Executes fractional synchronization loop between drive and response."""
    print(f"[*] Initializing Fractional Sliding Mode Synchronization for {total_steps} steps...")
    
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
        
        x_next = x_trajectory[i]
        y_pred = response_solver.predict(y0, valid_f_y)
        
        e_next = y_pred - config.GAMMA * x_next
        e_nu_next = e_next * np.power(e_next**2 + config.EPSILON, config.NU / 2.0)
        
        temp_e = np.vstack([valid_e, e_next])[-config.L:]
        temp_e_nu = np.vstack([valid_e_nu, e_nu_next])[-config.L:]
        
        I_e_next = e_integrator.integrate(temp_e)
        I_e_nu_next = e_nu_integrator.integrate(temp_e_nu)
        sigma_next = compute_sigma(e_next, I_e_next, I_e_nu_next, alpha=config.ALPHA, beta=config.BETA)
        
        sys_nonlin = compute_nonlinear_cancellation(x_next, y_pred, config.GAMMA, a=config.A, b=config.B)
        u_next = compute_control(e_next, sigma_next, sys_nonlin, 
                                 alpha=config.ALPHA, beta=config.BETA, theta=config.THETA, delta=config.DELTA, 
                                 nu=config.NU, mu=config.MU, epsilon=config.EPSILON, clip_limit=config.CLIP_LIMIT)
        
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
                
    return y_trajectory

def main():
    parser = argparse.ArgumentParser(description="Fractional Hyperchaotic Encryption Demo for Custom Images")
    parser.add_argument("-i", "--image", type=str, required=True, help="Path to the custom image file to encrypt")
    parser.add_argument("-m", "--mode", type=str, choices=["robust", "paper"], default="robust", 
                        help="Keystream derivation mode: 'robust' (SHA-256 + LCG) or 'paper' (Direct Quantization)")
    parser.add_argument("-s", "--size", type=int, default=256, help="Target resize dimension (default: 256 pixels)")
    args = parser.parse_args()
    
    # Override configuration mode
    config.MODE = args.mode
    
    # Create results folder if missing
    results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
    os.makedirs(results_dir, exist_ok=True)
    
    print("\n" + "="*60)
    print(f"    Fractional Chaotic Encryption Demo (MODE: {args.mode.upper()})")
    print("="*60)
    
    # 1. Load Image
    img_array = load_image(args.image, target_size=(args.size, args.size))
    img_shape = img_array.shape
    img_bytes = img_array.flatten()
    N = len(img_bytes)
    print(f"[*] Image resized to {img_shape} ({N} bytes)")
    
    # Discard transient steps + image size steps
    total_steps = config.DISCARD_STEPS + N
    
    # 2. Generate Drive Trajectory (Transmitter)
    t_start = time.time()
    print(f"[*] Simulating chaotic drive trajectory for {total_steps} steps...")
    x_traj = generate_fractional_sequences(total_steps, discard_transients=False)
    
    # 3. Synchronize Response Trajectory (Receiver)
    y_traj = run_synchronization(total_steps, x_traj)
    
    # Decouple synchronization transients
    x_sync = x_traj[config.DISCARD_STEPS : config.DISCARD_STEPS + N]
    y_sync = y_traj[config.DISCARD_STEPS : config.DISCARD_STEPS + N]
    
    # 4. Extract Cryptographic Keystreams
    print("[*] Extracting keys from synchronized trajectory states...")
    if args.mode == "paper":
        tx_keys = extract_paper_keys(x_sync)
        rx_keys = extract_paper_keys(y_sync)
    else:
        tx_keys = extract_keys(x_sync)
        rx_keys = extract_keys(y_sync)
        
    keys_match = np.array_equal(tx_keys, rx_keys)
    print(f"[*] Keystream Parity Check: {'PASSED (Bit-Identical)' if keys_match else 'FAILED'}")
    if not keys_match:
        print("[!] ERROR: Drive and Response keys do not match. Decryption will fail.")
        sys.exit(1)
        
    # 5. Image Encryption
    print("[*] Encrypting image (Permutation + Modulo Diffusion)...")
    t_enc_start = time.time()
    if args.mode == "paper":
        encrypted_bytes = encrypt_paper(img_bytes, x_sync)
    else:
        encrypted_bytes = encrypt_image(img_bytes, tx_keys)
    t_enc_end = time.time()
    enc_time = t_enc_end - t_enc_start
    
    # 6. Image Decryption
    print("[*] Decrypting image (Inverse Permutation + Inverse Diffusion)...")
    t_dec_start = time.time()
    if args.mode == "paper":
        decrypted_bytes = decrypt_paper(encrypted_bytes, y_sync)
    else:
        decrypted_bytes = decrypt_image(encrypted_bytes, rx_keys)
    t_dec_end = time.time()
    dec_time = t_dec_end - t_dec_start
    
    total_time = t_dec_end - t_start
    
    # Save encrypted & decrypted images
    enc_path = os.path.join(results_dir, "custom_encrypted.png")
    dec_path = os.path.join(results_dir, "custom_decrypted.png")
    
    Image.fromarray(encrypted_bytes.reshape(img_shape)).save(enc_path)
    Image.fromarray(decrypted_bytes.reshape(img_shape)).save(dec_path)
    print(f"[*] Saved encrypted image to: {enc_path}")
    print(f"[*] Saved decrypted image to: {dec_path}")
    
    # 7. Compute Quantitative Security Stats
    h_original = calculate_entropy(img_array)
    h_encrypted = calculate_entropy(encrypted_bytes.reshape(img_shape))
    
    _, _, corr_hor = get_adjacent_pairs(encrypted_bytes.reshape(img_shape), 'horizontal', num_samples=2000)
    _, _, corr_ver = get_adjacent_pairs(encrypted_bytes.reshape(img_shape), 'vertical', num_samples=2000)
    _, _, corr_diag = get_adjacent_pairs(encrypted_bytes.reshape(img_shape), 'diagonal', num_samples=2000)
    
    dec_match = np.array_equal(img_bytes, decrypted_bytes)
    
    # 8. Save Side-by-Side Comparison Plot
    fig, axes = plt.subplots(1, 3, figsize=(15, 6))
    axes[0].imshow(img_array, cmap='gray')
    axes[0].set_title("Original Plaintext")
    axes[0].axis('off')
    
    axes[1].imshow(encrypted_bytes.reshape(img_shape), cmap='gray')
    axes[1].set_title(f"Encrypted Ciphertext\n(Entropy: {h_encrypted:.4f})")
    axes[1].axis('off')
    
    axes[2].imshow(decrypted_bytes.reshape(img_shape), cmap='gray')
    axes[2].set_title(f"Decrypted Image\n(Success: {dec_match})")
    axes[2].axis('off')
    
    comp_path = os.path.join(results_dir, "custom_comparison.png")
    plt.tight_layout()
    plt.savefig(comp_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[*] Saved side-by-side comparison to: {comp_path}")
    
    # Print Quantitative Summary
    print("\n" + "="*60)
    print("    SECURITY & PERFORMANCE EVALUATION SUMMARY")
    print("="*60)
    print(f"Decryption Integrity Status  : {'SUCCESS (100% Bit-Identical)' if dec_match else 'FAILED'}")
    print(f"Original Image Entropy       : {h_original:.6f} bits")
    print(f"Encrypted Image Entropy      : {h_encrypted:.6f} bits (Target: >7.99)")
    print(f"Horizontal Pixel Correlation : {corr_hor:.6f}")
    print(f"Vertical Pixel Correlation   : {corr_ver:.6f}")
    print(f"Diagonal Pixel Correlation   : {corr_diag:.6f}")
    print(f"Encryption Time              : {enc_time:.4f} seconds")
    print(f"Decryption Time              : {dec_time:.4f} seconds")
    print(f"Total Simulation & Run Time  : {total_time:.2f} seconds")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
