import os
import sys
import time
import numpy as np
import pandas as pd
from PIL import Image

sys.path.append("/Users/archismanchoudhury/Desktop/research/Research Implementation")

import config
from fractional_core.abm_solver import ABMSolver
from chaos.drive_system import drive_field
from crypto.key_extractor import extract_keys
from crypto.image_cipher import encrypt_image
from paper_mode.direct_key_extractor import extract_paper_keys
from paper_mode.direct_encrypt import encrypt_paper

def generate_sequences_custom(length, x0=None, a=None, b=None):
    """Generates drive sequences with custom initial conditions or parameters."""
    if x0 is None:
        x0 = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0], dtype=np.float64)
    if a is None:
        a = config.A
    if b is None:
        b = config.B
        
    solver = ABMSolver(q=config.Q, dt=config.DT, truncation_window=config.L, dim=6)
    f_history = np.zeros((config.L, 6), dtype=np.float64)
    f_history[0] = drive_field(x0, a=a, b=b)
    
    trajectory = np.zeros((length, 6), dtype=np.float64)
    trajectory[0] = x0
    n_hist = 1
    
    for i in range(1, length):
        valid_f_hist = f_history[:n_hist]
        x_pred = solver.predict(x0, valid_f_hist)
        f_pred = drive_field(x_pred, a=a, b=b)
        x_next = solver.correct(x0, valid_f_hist, f_pred)
        f_next = drive_field(x_next, a=a, b=b)
        trajectory[i] = x_next
        
        if n_hist < config.L:
            f_history[n_hist] = f_next
            n_hist += 1
        else:
            f_history[:-1] = f_history[1:]
            f_history[-1] = f_next
            
    return trajectory

def compute_entropy(img_array):
    hist, _ = np.histogram(img_array, bins=256, range=(0, 256))
    hist = hist[hist > 0]
    probabilities = hist / np.sum(hist)
    return -np.sum(probabilities * np.log2(probabilities))

def compute_npcr_uaci(c1, c2):
    N = len(c1)
    npcr = (np.sum(c1 != c2) / N) * 100.0
    uaci = np.mean(np.abs(c1.astype(np.float64) - c2.astype(np.float64)) / 255.0) * 100.0
    return npcr, uaci

def main():
    base_dir = "/Users/archismanchoudhury/Desktop/research/Research Implementation"
    lena_path = os.path.join(base_dir, "images", "lena.png")
    output_path = os.path.join(base_dir, "evaluation", "key_sensitivity_comparison.csv")
    
    img = Image.open(lena_path).convert('L')
    img_bytes = np.array(img, dtype=np.uint8).flatten()
    N = len(img_bytes)
    total_steps = config.DISCARD_STEPS + N
    
    print("[*] Generating base trajectories for sensitivity test...")
    # Base parameters
    x0_base = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0], dtype=np.float64)
    x_traj_base = generate_sequences_custom(total_steps, x0=x0_base)
    x_sync_base = x_traj_base[config.DISCARD_STEPS:]
    
    # ------------------ ROBUST MODE ------------------
    print("[*] Testing ROBUST mode sensitivity...")
    tx_keys_base_r = extract_keys(x_sync_base)
    cipher_base_r = encrypt_image(img_bytes, tx_keys_base_r)
    entropy_base_r = compute_entropy(cipher_base_r)
    
    # Test 1: One-bit key change
    # In Robust Mode, we perturb the key seed by flipping 1 bit.
    # To do this, we manually implement key generation with 1-bit perturbed seed.
    # In crypto/key_extractor.py, the seed is hashlib.sha256(byte_array).digest().
    # We can fetch the seed_ints from extract_keys flow and pertub it.
    # To keep it simple, we flip 1 bit in the PRNG's keys[0, 0] before encryption.
    # Wait, the prompt says 'One-bit key change'. Let's do a 1-bit key change in the final key matrix:
    tx_keys_perturbed_r = np.copy(tx_keys_base_r)
    tx_keys_perturbed_r[0, 0] ^= 1 # flip LSB of first key element
    cipher_key_r = encrypt_image(img_bytes, tx_keys_perturbed_r)
    diff_key_r = (np.sum(cipher_base_r != cipher_key_r) / N) * 100.0
    entropy_key_r = compute_entropy(cipher_key_r)
    npcr_key_r, uaci_key_r = compute_npcr_uaci(cipher_base_r, cipher_key_r)
    
    # Test 2: Initial Condition Perturbation (x1_0 + 1e-14)
    x0_perturbed = x0_base.copy()
    x0_perturbed[0] += 1e-14
    x_traj_ic = generate_sequences_custom(total_steps, x0=x0_perturbed)
    x_sync_ic = x_traj_ic[config.DISCARD_STEPS:]
    tx_keys_ic_r = extract_keys(x_sync_ic)
    cipher_ic_r = encrypt_image(img_bytes, tx_keys_ic_r)
    diff_ic_r = (np.sum(cipher_base_r != cipher_ic_r) / N) * 100.0
    entropy_ic_r = compute_entropy(cipher_ic_r)
    npcr_ic_r, uaci_ic_r = compute_npcr_uaci(cipher_base_r, cipher_ic_r)
    
    # Test 3: Parameter Perturbation (a + 1e-14)
    x_traj_param = generate_sequences_custom(total_steps, x0=x0_base, a=config.A + 1e-14)
    x_sync_param = x_traj_param[config.DISCARD_STEPS:]
    tx_keys_param_r = extract_keys(x_sync_param)
    cipher_param_r = encrypt_image(img_bytes, tx_keys_param_r)
    diff_param_r = (np.sum(cipher_base_r != cipher_param_r) / N) * 100.0
    entropy_param_r = compute_entropy(cipher_param_r)
    npcr_param_r, uaci_param_r = compute_npcr_uaci(cipher_base_r, cipher_param_r)
    
    # ------------------ PAPER MODE ------------------
    print("[*] Testing PAPER mode sensitivity...")
    cipher_base_p = encrypt_paper(img_bytes, x_sync_base)
    entropy_base_p = compute_entropy(cipher_base_p)
    
    # Test 1: One-bit key change
    # In Paper Mode, we manually flip 1 bit of the extracted key sequence keys[0, 0] ^= 1.
    # Since encrypt_paper takes states and extracts keys internally, we modify the key matrix inside
    # a local encrypt_paper_perturbed function:
    tx_keys_base_p = extract_paper_keys(x_sync_base)
    tx_keys_perturbed_p = np.copy(tx_keys_base_p)
    tx_keys_perturbed_p[0, 0] ^= 1 # flip LSB of first key element
    
    # Local encrypt with keys
    perm_indices = np.argsort(tx_keys_perturbed_p[:N, 0], kind='stable')
    permuted_bytes = img_bytes[perm_indices].astype(np.int32)
    k = tx_keys_perturbed_p[:N, 3].astype(np.int32)
    c_forward = np.zeros(N, dtype=np.int32)
    curr = 0
    for i in range(N):
        curr = (permuted_bytes[i] + k[i] + curr) % 256
        c_forward[i] = curr
    c_backward = np.zeros(N, dtype=np.int32)
    curr = 0
    for i in range(N - 1, -1, -1):
        curr = (c_forward[i] + k[i] + curr) % 256
        c_backward[i] = curr
    cipher_key_p = c_backward.astype(np.uint8)
    
    diff_key_p = (np.sum(cipher_base_p != cipher_key_p) / N) * 100.0
    entropy_key_p = compute_entropy(cipher_key_p)
    npcr_key_p, uaci_key_p = compute_npcr_uaci(cipher_base_p, cipher_key_p)
    
    # Test 2: Initial Condition Perturbation (x1_0 + 1e-14)
    cipher_ic_p = encrypt_paper(img_bytes, x_sync_ic)
    diff_ic_p = (np.sum(cipher_base_p != cipher_ic_p) / N) * 100.0
    entropy_ic_p = compute_entropy(cipher_ic_p)
    npcr_ic_p, uaci_ic_p = compute_npcr_uaci(cipher_base_p, cipher_ic_p)
    
    # Test 3: Parameter Perturbation (a + 1e-14)
    cipher_param_p = encrypt_paper(img_bytes, x_sync_param)
    diff_param_p = (np.sum(cipher_base_p != cipher_param_p) / N) * 100.0
    entropy_param_p = compute_entropy(cipher_param_p)
    npcr_param_p, uaci_param_p = compute_npcr_uaci(cipher_base_p, cipher_param_p)
    
    # Save results to DataFrame
    df_data = [
        {
            "Test_Case": "1-bit Key Change",
            "Robust_Diff_%": diff_key_r,
            "Robust_Entropy_Change": abs(entropy_base_r - entropy_key_r),
            "Robust_NPCR_%": npcr_key_r,
            "Robust_UACI_%": uaci_key_r,
            "Paper_Diff_%": diff_key_p,
            "Paper_Entropy_Change": abs(entropy_base_p - entropy_key_p),
            "Paper_NPCR_%": npcr_key_p,
            "Paper_UACI_%": uaci_key_p
        },
        {
            "Test_Case": "IC Perturbation (1e-14)",
            "Robust_Diff_%": diff_ic_r,
            "Robust_Entropy_Change": abs(entropy_base_r - entropy_ic_r),
            "Robust_NPCR_%": npcr_ic_r,
            "Robust_UACI_%": uaci_ic_r,
            "Paper_Diff_%": diff_ic_p,
            "Paper_Entropy_Change": abs(entropy_base_p - entropy_ic_p),
            "Paper_NPCR_%": npcr_ic_p,
            "Paper_UACI_%": uaci_ic_p
        },
        {
            "Test_Case": "Parameter Perturbation (1e-14)",
            "Robust_Diff_%": diff_param_r,
            "Robust_Entropy_Change": abs(entropy_base_r - entropy_param_r),
            "Robust_NPCR_%": npcr_param_r,
            "Robust_UACI_%": uaci_param_r,
            "Paper_Diff_%": diff_param_p,
            "Paper_Entropy_Change": abs(entropy_base_p - entropy_param_p),
            "Paper_NPCR_%": npcr_param_p,
            "Paper_UACI_%": uaci_param_p
        }
    ]
    
    df = pd.DataFrame(df_data)
    df.to_csv(output_path, index=False)
    print(f"[+] Key sensitivity test completed. Saved results to {output_path}")

if __name__ == "__main__":
    main()
