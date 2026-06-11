import numpy as np

def calculate_npcr_uaci(cipher1, cipher2):
    """
    Computes NPCR (Number of Pixels Change Rate) and UACI (Unified Average Changing Intensity).
    Both inputs must be numpy arrays of the same shape.
    """
    # Flatten arrays
    c1 = cipher1.ravel().astype(np.float64)
    c2 = cipher2.ravel().astype(np.float64)
    total_pixels = len(c1)
    
    # 1. NPCR
    different_pixels = np.sum(c1 != c2)
    npcr = (different_pixels / total_pixels) * 100.0
    
    # 2. UACI
    uaci = (np.sum(np.abs(c1 - c2)) / (total_pixels * 255.0)) * 100.0
    
    return npcr, uaci

def run_npcr_uaci_analysis(original_img, key, encrypt_func, output_path):
    """
    Runs the NPCR & UACI test.
    Perturbs a single pixel in the original image, encrypts both,
    and calculates NPCR & UACI between the resulting ciphertexts.
    """
    # Flatten plaintext
    flat_orig = original_img.ravel().copy()
    
    # Encrypt original
    cipher1 = encrypt_func(flat_orig, key)
    
    # Perturb exactly one pixel (e.g. the center pixel)
    idx_to_perturb = len(flat_orig) // 2
    flat_perturbed = flat_orig.copy()
    flat_perturbed[idx_to_perturb] = (int(flat_perturbed[idx_to_perturb]) + 1) % 256
    
    # Encrypt perturbed
    cipher2 = encrypt_func(flat_perturbed, key)
    
    # Calculate NPCR and UACI
    npcr, uaci = calculate_npcr_uaci(cipher1, cipher2)
    
    with open(output_path, 'w') as f:
        f.write("=== NPCR & UACI ANALYSIS REPORT ===\n\n")
        f.write(f"NPCR (Number of Pixels Change Rate): {npcr:.6f}%\n")
        f.write(f"Target NPCR (>99%):                   {'PASSED' if npcr > 99.0 else 'FAILED'}\n\n")
        f.write(f"UACI (Unified Average Changing Intensity): {uaci:.6f}%\n")
        f.write(f"Target UACI (~33.46%):                     {'PASSED' if abs(uaci - 33.46) < 1.0 else 'CHECK'}\n")
        
    print(f"Saved NPCR & UACI report to {output_path} (NPCR: {npcr:.4f}%, UACI: {uaci:.4f}%)")
    return npcr, uaci
