import os
import sys
import time
import resource
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

def get_peak_memory_mb():
    """Returns the peak memory usage in Megabytes."""
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # On macOS, ru_maxrss is in bytes, on Linux it is in kilobytes.
    # macOS: divide by 1024 * 1024
    if sys.platform == 'darwin':
        return usage / (1024 * 1024)
    else:
        return usage / 1024

def main():
    base_dir = "/Users/archismanchoudhury/Desktop/research/Research Implementation"
    lena_path = os.path.join(base_dir, "images", "lena.png")
    output_path = os.path.join(base_dir, "evaluation", "performance_results.csv")
    
    img = Image.open(lena_path).convert('L')
    img_bytes = np.array(img, dtype=np.uint8).flatten()
    N = len(img_bytes)
    size_mb = N / (1024 * 1024)
    
    total_steps = config.DISCARD_STEPS + N
    
    # 1. Benchmark trajectory generation + synchronization
    print("[*] Benchmarking Trajectory Generation and Synchronization...")
    t0 = time.time()
    x_traj = generate_fractional_sequences(total_steps, discard_transients=False)
    sync_t0 = time.time()
    y_traj = run_synchronization(total_steps, x_traj)
    sync_time = time.time() - sync_t0
    total_sim_time = time.time() - t0
    
    x_sync = x_traj[config.DISCARD_STEPS:]
    y_sync = y_traj[config.DISCARD_STEPS:]
    
    # 2. Benchmark Robust Mode (averaged over 20 runs)
    print("[*] Benchmarking ROBUST mode throughput...")
    tx_keys_r = extract_keys(x_sync)
    rx_keys_r = extract_keys(y_sync)
    
    enc_times_r = []
    dec_times_r = []
    
    for _ in range(20):
        t0 = time.time()
        c_r = encrypt_image(img_bytes, tx_keys_r)
        enc_times_r.append(time.time() - t0)
        
        t0 = time.time()
        _ = decrypt_image(c_r, rx_keys_r)
        dec_times_r.append(time.time() - t0)
        
    avg_enc_time_r = np.mean(enc_times_r)
    avg_dec_time_r = np.mean(dec_times_r)
    
    throughput_enc_r = size_mb / avg_enc_time_r
    throughput_dec_r = size_mb / avg_dec_time_r
    
    mem_r = get_peak_memory_mb()
    
    # 3. Benchmark Paper Mode (averaged over 20 runs)
    print("[*] Benchmarking PAPER mode throughput...")
    
    enc_times_p = []
    dec_times_p = []
    
    for _ in range(20):
        t0 = time.time()
        c_p = encrypt_paper(img_bytes, x_sync)
        enc_times_p.append(time.time() - t0)
        
        t0 = time.time()
        _ = decrypt_paper(c_p, y_sync)
        dec_times_p.append(time.time() - t0)
        
    avg_enc_time_p = np.mean(enc_times_p)
    avg_dec_time_p = np.mean(dec_times_p)
    
    throughput_enc_p = size_mb / avg_enc_time_p
    throughput_dec_p = size_mb / avg_dec_time_p
    
    mem_p = get_peak_memory_mb()
    
    # Save results to CSV
    results = [
        {
            "Mode": "robust",
            "Encryption_Time_Avg_s": avg_enc_time_r,
            "Decryption_Time_Avg_s": avg_dec_time_r,
            "Encryption_Throughput_MBs": throughput_enc_r,
            "Decryption_Throughput_MBs": throughput_dec_r,
            "Peak_Process_Memory_MB": mem_r,
            "Synchronization_Time_s": sync_time,
            "Total_Simulation_Time_s": total_sim_time
        },
        {
            "Mode": "paper",
            "Encryption_Time_Avg_s": avg_enc_time_p,
            "Decryption_Time_Avg_s": avg_dec_time_p,
            "Encryption_Throughput_MBs": throughput_enc_p,
            "Decryption_Throughput_MBs": throughput_dec_p,
            "Peak_Process_Memory_MB": mem_p,
            "Synchronization_Time_s": sync_time,
            "Total_Simulation_Time_s": total_sim_time
        }
    ]
    
    df = pd.DataFrame(results)
    df.to_csv(output_path, index=False)
    print(f"[+] Performance benchmark completed. Saved results to {output_path}")
    print("\n--- RESULTS OVERVIEW ---")
    print(f"Robust Encryption: {throughput_enc_r:.2f} MB/s | Decryption: {throughput_dec_r:.2f} MB/s")
    print(f"Paper Encryption:  {throughput_enc_p:.2f} MB/s | Decryption: {throughput_dec_p:.2f} MB/s")
    
if __name__ == "__main__":
    main()
