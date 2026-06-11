import os
import sys
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

def main():
    base_dir = "/Users/archismanchoudhury/Desktop/research/Research Implementation"
    lena_path = os.path.join(base_dir, "images", "lena.png")
    output_path = os.path.join(base_dir, "evaluation", "robustness_results.csv")
    
    img = Image.open(lena_path).convert('L')
    img_bytes = np.array(img, dtype=np.uint8).flatten()
    N = len(img_bytes)
    total_steps = config.DISCARD_STEPS + N
    
    # 1. Run nominal synchronization
    print("[*] Generating trajectories for robustness study...")
    x_traj = generate_fractional_sequences(total_steps, discard_transients=False)
    y_traj = run_synchronization(total_steps, x_traj)
    
    x_sync = x_traj[config.DISCARD_STEPS:]
    y_sync = y_traj[config.DISCARD_STEPS:]
    
    # Nominal Encryptions and Key Extractions
    tx_keys_r = extract_keys(x_sync)
    cipher_r = encrypt_image(img_bytes, tx_keys_r)
    
    tx_keys_p = extract_paper_keys(x_sync)
    cipher_p = encrypt_paper(img_bytes, x_sync)
    
    noise_sigmas = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2]
    results = []
    
    print("=== ROBUSTNESS BENCHMARK ===")
    for sigma in noise_sigmas:
        # Inject Gaussian noise
        rng = np.random.default_rng(42)
        noise = rng.normal(0, sigma, size=y_sync.shape)
        perturbed_y = y_sync + noise
        
        # Calculate synchronization stability as RMSE
        rmse = np.sqrt(np.mean((perturbed_y - x_sync) ** 2))
        
        # --- ROBUST MODE ---
        rx_keys_r = extract_keys(perturbed_y)
        parity_r = (np.sum(tx_keys_r == rx_keys_r) / tx_keys_r.size) * 100.0
        try:
            dec_r = decrypt_image(cipher_r, rx_keys_r)
            dec_success_r = np.array_equal(img_bytes, dec_r)
        except Exception:
            dec_success_r = False
            
        # --- PAPER MODE ---
        rx_keys_p = extract_paper_keys(perturbed_y)
        parity_p = (np.sum(tx_keys_p == rx_keys_p) / tx_keys_p.size) * 100.0
        try:
            dec_p = decrypt_paper(cipher_p, perturbed_y)
            dec_success_p = np.array_equal(img_bytes, dec_p)
        except Exception:
            dec_success_p = False
            
        print(f"Sigma {sigma:.0e} -> RMSE: {rmse:.6e}")
        print(f"  Robust: Parity {parity_r:.2f}% | Dec Success: {dec_success_r}")
        print(f"  Paper:  Parity {parity_p:.2f}% | Dec Success: {dec_success_p}")
        
        results.append({
            "Sigma": sigma,
            "RMSE": rmse,
            "Robust_Key_Parity_%": parity_r,
            "Robust_Dec_Success": str(dec_success_r),
            "Paper_Key_Parity_%": parity_p,
            "Paper_Dec_Success": str(dec_success_p)
        })
        
    df = pd.DataFrame(results)
    df.to_csv(output_path, index=False)
    print(f"Saved robustness results to {output_path}")

if __name__ == "__main__":
    main()
