import numpy as np

def calculate_entropy(img):
    """
    Computes Shannon Information Entropy for a 2D grayscale image.
    H = - sum( p(i) * log2(p(i)) )
    """
    flat = img.ravel()
    total_pixels = len(flat)
    
    # Calculate frequencies of each pixel value (0-255)
    counts = np.bincount(flat, minlength=256)
    probs = counts / total_pixels
    
    # Filter out 0 probabilities to avoid log2(0)
    probs = probs[probs > 0]
    
    # Compute Shannon Entropy
    entropy = -np.sum(probs * np.log2(probs))
    return entropy

def run_entropy_analysis(original_img, encrypted_img, output_path):
    """
    Runs entropy analysis and writes the text report.
    """
    h_orig = calculate_entropy(original_img)
    h_enc = calculate_entropy(encrypted_img)
    max_entropy = 8.0
    
    orig_pct = (h_orig / max_entropy) * 100
    enc_pct = (h_enc / max_entropy) * 100
    
    with open(output_path, 'w') as f:
        f.write("=== INFORMATION ENTROPY ANALYSIS REPORT ===\n\n")
        f.write(f"Original Image Entropy:  {h_orig:.6f} bits\n")
        f.write(f"Theoretical Max:         {max_entropy:.6f} bits\n")
        f.write(f"Percentage of Max:       {orig_pct:.4f}%\n\n")
        f.write(f"Encrypted Image Entropy: {h_enc:.6f} bits\n")
        f.write(f"Theoretical Max:         {max_entropy:.6f} bits\n")
        f.write(f"Percentage of Max:       {enc_pct:.4f}%\n\n")
        f.write(f"Entropy Target (>7.99):  {'PASSED' if h_enc > 7.99 else 'FAILED'}\n")
        
    print(f"Saved entropy report to {output_path} (Encrypted Entropy: {h_enc:.6f})")
    return h_orig, h_enc
