import sys
import os
import numpy as np
from PIL import Image

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from main.run_crypto import run_synchronization
from crypto.key_extractor import extract_keys
from crypto.image_cipher import encrypt_image

def load_image_as_array(filepath, size=None):
    img = Image.open(filepath).convert('L')
    if size:
        img = img.resize(size)
    return np.array(img, dtype=np.uint8).flatten()

def compute_entropy(img_array):
    """
    Computes the Shannon entropy of an image array.
    H(s) = - sum( p(si) * log2( p(si) ) )
    """
    hist, _ = np.histogram(img_array, bins=256, range=(0, 256))
    hist = hist[hist > 0] # Avoid log(0)
    probabilities = hist / np.sum(hist)
    entropy = -np.sum(probabilities * np.log2(probabilities))
    return entropy

def compute_npcr_uaci(img_bytes, keys):
    """
    Computes NPCR and UACI by flipping a single pixel and comparing ciphertexts.
    """
    # 1. Base Encryption
    C1 = encrypt_image(img_bytes, keys)
    
    # 2. Perturbation
    img_perturbed = np.copy(img_bytes)
    img_perturbed[0] ^= 1 # Flip LSB of the very first pixel
    
    # 3. Perturbed Encryption
    C2 = encrypt_image(img_perturbed, keys)
    
    # 4. NPCR Computation
    diff_pixels = np.sum(C1 != C2)
    total_pixels = len(img_bytes)
    npcr = (diff_pixels / total_pixels) * 100.0
    
    # 5. UACI Computation
    diff_intensity = np.abs(C1.astype(np.float64) - C2.astype(np.float64))
    uaci = np.mean(diff_intensity / 255.0) * 100.0
    
    return npcr, uaci

def main():
    print("=== Fractional-Order Hyperchaotic Security Metrics ===")
    
    # Define paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    original_path = os.path.join(base_dir, 'images', 'test.png')
    encrypted_path = os.path.join(base_dir, 'results', 'encrypted.png')
    output_path = os.path.join(base_dir, 'results', 'security_metrics.txt')
    
    if not os.path.exists(encrypted_path):
        print(f"[!] Error: Encrypted image not found at {encrypted_path}")
        print("Please run main/run_crypto.py first.")
        sys.exit(1)
        
    # Load encrypted image for dimensions
    enc_img = Image.open(encrypted_path).convert('L')
    enc_shape = enc_img.size
    enc_array = np.array(enc_img, dtype=np.uint8).flatten()
    
    # Load original image
    orig_array = load_image_as_array(original_path, size=enc_shape)
    
    # 1. ENTROPY
    print("Computing Information Entropy...")
    orig_entropy = compute_entropy(orig_array)
    enc_entropy = compute_entropy(enc_array)
    print(f"Original Entropy : {orig_entropy:.4f}")
    print(f"Encrypted Entropy: {enc_entropy:.4f}")
    
    # 2. NPCR & UACI
    print("Generating chaotic keys for plaintext sensitivity analysis...")
    N = len(orig_array)
    total_steps = config.DISCARD_STEPS + N
    
    # Suppress output from run_synchronization to keep console clean
    import io
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        x_traj, _ = run_synchronization(total_steps)
    finally:
        sys.stdout = old_stdout
        
    x_sync = x_traj[config.DISCARD_STEPS : config.DISCARD_STEPS + N]
    tx_keys = extract_keys(np.round(x_sync, 1))
    
    print("Computing NPCR and UACI...")
    npcr, uaci = compute_npcr_uaci(orig_array, tx_keys)
    print(f"NPCR: {npcr:.4f}%")
    print(f"UACI: {uaci:.4f}%")
    
    # 3. VERDICT AND SAVING
    print("Saving metrics...")
    
    with open(output_path, 'w') as f:
        f.write("=== Fractional-Order Hyperchaotic Image Cipher Security Metrics ===\n\n")
        
        f.write("[ Information Entropy ]\n")
        f.write("Measures the randomness and statistical diffusion of the cipher.\n")
        f.write(f"Original Image Entropy  : {orig_entropy:.4f}\n")
        f.write(f"Encrypted Image Entropy : {enc_entropy:.4f} (Target ~7.99)\n\n")
        
        f.write("[ Plaintext Sensitivity (Differential Attack Resistance) ]\n")
        f.write("Evaluates the avalanche effect by perturbing exactly 1 bit of the original image.\n")
        f.write(f"NPCR (Number of Pixel Change Rate)      : {npcr:.4f}% (Target > 99%)\n")
        f.write(f"UACI (Unified Average Changing Intensity): {uaci:.4f}% (Target ~33%)\n\n")
        
        f.write("=== Conclusion ===\n")
        if enc_entropy > 7.9 and npcr > 99.0 and 30.0 < uaci < 35.0:
            f.write("The synchronized fractional-order hyperchaotic cipher demonstrates strong statistical diffusion and plaintext sensitivity.\n")
        else:
            f.write("The metrics deviate from ideal random behavior. Review the diffusion/confusion parameters.\n")
            
    print(f"Metrics successfully saved to: {output_path}")
    print("======================================================")

if __name__ == "__main__":
    main()
