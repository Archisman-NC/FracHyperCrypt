import os
import sys
import time
import numpy as np
import pandas as pd
from PIL import Image

sys.path.append("/Users/archismanchoudhury/Desktop/research/Research Implementation")

import config
from fractional_core.generator import generate_fractional_sequences
from main.run_crypto import run_synchronization
from crypto.key_extractor import extract_keys
from crypto.image_cipher import encrypt_image, decrypt_image
from paper_mode.direct_key_extractor import extract_paper_keys
from paper_mode.direct_encrypt import encrypt_paper
from paper_mode.direct_decrypt import decrypt_paper

def compute_entropy(img_array):
    hist, _ = np.histogram(img_array, bins=256, range=(0, 256))
    hist = hist[hist > 0]
    probabilities = hist / np.sum(hist)
    return -np.sum(probabilities * np.log2(probabilities))

def compute_correlation(img_array, direction):
    img = img_array.reshape(256, 256).astype(np.float64)
    if direction == 'horizontal':
        x = img[:, :-1].flatten()
        y = img[:, 1:].flatten()
    elif direction == 'vertical':
        x = img[:-1, :].flatten()
        y = img[1:, :].flatten()
    elif direction == 'diagonal':
        x = img[:-1, :-1].flatten()
        y = img[1:, 1:].flatten()
    else:
        return 0.0
    corr = np.corrcoef(x, y)
    return corr[0, 1] if not np.isnan(corr).any() else 0.0

def main():
    base_dir = "/Users/archismanchoudhury/Desktop/research/Research Implementation"
    images_dir = os.path.join(base_dir, "images")
    output_dir = os.path.join(base_dir, "evaluation")
    os.makedirs(output_dir, exist_ok=True)
    
    images = ["lena", "baboon", "peppers", "cameraman", "house"]
    N = 256 * 256
    total_steps = config.DISCARD_STEPS + N
    
    # 1. RUN TRAJECTORY GENERATION AND SYNCHRONIZATION ONCE
    print("[*] Generating fractional drive trajectory and synchronizing response system...")
    t0 = time.time()
    x_traj = generate_fractional_sequences(total_steps, discard_transients=False)
    sync_t0 = time.time()
    y_traj = run_synchronization(total_steps, x_traj)
    sync_time = time.time() - sync_t0
    total_trajectory_time = time.time() - t0
    print(f"[+] Synchronization completed in {sync_time:.2f}s (Total traj generation: {total_trajectory_time:.2f}s)")
    
    x_sync = x_traj[config.DISCARD_STEPS : config.DISCARD_STEPS + N]
    y_sync = y_traj[config.DISCARD_STEPS : config.DISCARD_STEPS + N]
    
    # 2. KEY GENERATION TIME
    print("[*] Benchmarking Key Generation...")
    # Robust keys
    t0 = time.time()
    tx_keys_r = extract_keys(x_sync)
    rx_keys_r = extract_keys(y_sync)
    key_gen_time_r = (time.time() - t0) / 2.0 # average per side
    
    # Paper keys
    t0 = time.time()
    tx_keys_p = extract_paper_keys(x_sync)
    rx_keys_p = extract_paper_keys(y_sync)
    key_gen_time_p = (time.time() - t0) / 2.0
    
    results = []
    
    for img_name in images:
        img_path = os.path.join(images_dir, f"{img_name}.png")
        print(f"\n[*] Processing image: {img_name} ({img_path})...")
        img = Image.open(img_path).convert('L')
        img_bytes = np.array(img, dtype=np.uint8).flatten()
        
        # --- ROBUST MODE ---
        print("  - Running ROBUST mode...")
        # Encryption
        t0 = time.time()
        c_r = encrypt_image(img_bytes, tx_keys_r)
        enc_time_r = time.time() - t0
        
        # Decryption
        t0 = time.time()
        d_r = decrypt_image(c_r, rx_keys_r)
        dec_time_r = time.time() - t0
        
        dec_success_r = np.array_equal(img_bytes, d_r)
        entropy_r = compute_entropy(c_r)
        h_corr_r = compute_correlation(c_r, 'horizontal')
        v_corr_r = compute_correlation(c_r, 'vertical')
        d_corr_r = compute_correlation(c_r, 'diagonal')
        
        # NPCR/UACI (plaintext sensitivity)
        img_perturbed = np.copy(img_bytes)
        img_perturbed[0] ^= 1
        c_perturbed_r = encrypt_image(img_perturbed, tx_keys_r)
        npcr_r = (np.sum(c_r != c_perturbed_r) / N) * 100.0
        uaci_r = np.mean(np.abs(c_r.astype(np.float64) - c_perturbed_r.astype(np.float64)) / 255.0) * 100.0
        
        results.append({
            "Image": img_name.capitalize(),
            "Mode": "robust",
            "Entropy": entropy_r,
            "NPCR": npcr_r,
            "UACI": uaci_r,
            "H_Corr": h_corr_r,
            "V_Corr": v_corr_r,
            "D_Corr": d_corr_r,
            "Enc_Time": enc_time_r,
            "Dec_Time": dec_time_r,
            "Sync_Time": sync_time,
            "Key_Gen_Time": key_gen_time_r,
            "Dec_Success": dec_success_r
        })
        
        # --- PAPER MODE ---
        print("  - Running PAPER mode...")
        # Encryption
        t0 = time.time()
        c_p = encrypt_paper(img_bytes, x_sync)
        enc_time_p = time.time() - t0
        
        # Decryption
        t0 = time.time()
        d_p = decrypt_paper(c_p, y_sync)
        dec_time_p = time.time() - t0
        
        dec_success_p = np.array_equal(img_bytes, d_p)
        entropy_p = compute_entropy(c_p)
        h_corr_p = compute_correlation(c_p, 'horizontal')
        v_corr_p = compute_correlation(c_p, 'vertical')
        d_corr_p = compute_correlation(c_p, 'diagonal')
        
        # NPCR/UACI (plaintext sensitivity)
        c_perturbed_p = encrypt_paper(img_perturbed, x_sync)
        npcr_p = (np.sum(c_p != c_perturbed_p) / N) * 100.0
        uaci_p = np.mean(np.abs(c_p.astype(np.float64) - c_perturbed_p.astype(np.float64)) / 255.0) * 100.0
        
        results.append({
            "Image": img_name.capitalize(),
            "Mode": "paper",
            "Entropy": entropy_p,
            "NPCR": npcr_p,
            "UACI": uaci_p,
            "H_Corr": h_corr_p,
            "V_Corr": v_corr_p,
            "D_Corr": d_corr_p,
            "Enc_Time": enc_time_p,
            "Dec_Time": dec_time_p,
            "Sync_Time": sync_time,
            "Key_Gen_Time": key_gen_time_p,
            "Dec_Success": dec_success_p
        })
        
    df = pd.DataFrame(results)
    csv_path = os.path.join(output_dir, "benchmark_results.csv")
    df.to_csv(csv_path, index=False)
    print(f"\n[+] Benchmark complete. Saved results to {csv_path}")

if __name__ == "__main__":
    main()
