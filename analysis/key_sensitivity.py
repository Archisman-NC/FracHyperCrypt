import os
import numpy as np
import matplotlib.pyplot as plt
import hashlib
import config
from crypto.key_extractor import extract_keys

def extract_perturbed_keys(sync_states):
    """
    Extracts alternative keys by flipping exactly one bit in the SHA-256 seed.
    """
    N = len(sync_states)
    block_size = 32
    num_blocks = max(1, N // block_size)
    
    bits = []
    # Use states x2, x3, x4, x5, x6 which are highly stable and synchronized
    for j in [1, 2, 3, 4, 5]:
        for b in range(num_blocks):
            start = b * block_size
            end = start + block_size
            votes = np.sum(sync_states[start:end, j] > 0)
            bit = 1 if votes > (block_size / 2) else 0
            bits.append(bit)
            
    # Convert bits to bytes
    byte_array = bytearray()
    bit_string = "".join(str(b) for b in bits)
    for i in range(0, len(bit_string), 8):
        byte_chunk = bit_string[i:i+8]
        if len(byte_chunk) < 8:
            byte_chunk = byte_chunk.ljust(8, '0')
        byte_array.append(int(byte_chunk, 2))
        
    # Generate 256-bit seed
    seed = hashlib.sha256(byte_array).digest()
    
    # Convert bytes to sequence of uint32 for SeedSequence compatibility
    seed_ints = np.frombuffer(seed, dtype=np.uint32).copy()
    
    # Flip exactly one bit in the seed (LSB of the first 32-bit integer)
    seed_ints[0] ^= 1
    
    # Expand seed to generate keys of shape (N, 6)
    rng = np.random.default_rng(seed_ints)
    keys = rng.integers(0, 256, size=(N, 6), dtype=np.uint8)
    return keys

def run_key_sensitivity_analysis(original_img, x_sync, encrypt_func, output_path):
    """
    Encrypts the image using standard keys and keys with a 1-bit difference in their seed,
    then generates comparison and difference plots.
    """
    img_bytes = original_img.ravel()
    N = len(img_bytes)
    
    # 1. Encrypt with standard keys
    tx_keys = extract_keys(x_sync)
    cipher1 = encrypt_func(img_bytes, tx_keys)
    
    # 2. Encrypt with perturbed keys (1 bit flipped in seed)
    print("Generating keys with 1-bit seed perturbation...")
    perturbed_keys = extract_perturbed_keys(x_sync)
    cipher2 = encrypt_func(img_bytes, perturbed_keys)
    
    # 3. Compute difference stats
    pixel_diffs = np.sum(cipher1 != cipher2)
    pct_diff = (pixel_diffs / N) * 100.0
    avg_intensity_diff = np.mean(np.abs(cipher1.astype(np.float64) - cipher2.astype(np.float64)))
    
    # 4. Generate comparison and difference plot
    img_shape = original_img.shape
    c1_img = cipher1.reshape(img_shape)
    c2_img = cipher2.reshape(img_shape)
    diff_img = np.abs(c1_img.astype(np.float64) - c2_img.astype(np.float64)).astype(np.uint8)
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.5))
    
    axes[0].imshow(c1_img, cmap='gray')
    axes[0].set_title("Ciphertext 1 (Standard Key)", fontsize=12)
    axes[0].axis('off')
    
    axes[1].imshow(c2_img, cmap='gray')
    axes[1].set_title("Ciphertext 2 (1-Bit Key Difference)", fontsize=12)
    axes[1].axis('off')
    
    axes[2].imshow(diff_img, cmap='gray')
    axes[2].set_title(f"Absolute Difference\n(Diff: {pct_diff:.2f}%)", fontsize=12)
    axes[2].axis('off')
    
    fig.suptitle("Key Sensitivity Analysis", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Saved key sensitivity plot to {output_path} (Ciphertext Difference: {pct_diff:.2f}%)")
    return pct_diff, avg_intensity_diff
