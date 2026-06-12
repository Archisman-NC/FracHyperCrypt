import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

def load_image_as_array(filepath, size=None):
    """Loads a grayscale image and optionally resizes it."""
    img = Image.open(filepath).convert('L')
    if size:
        img = img.resize(size)
    return np.array(img, dtype=np.uint8).flatten()

def main():
    print("=== Fractional-Order Hyperchaotic Histogram Analysis ===")
    
    # Define paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    original_path = os.path.join(base_dir, 'images', 'test.png')
    encrypted_path = os.path.join(base_dir, 'results', 'encrypted.png')
    output_path = os.path.join(base_dir, 'results', 'histogram_analysis.png')
    
    if not os.path.exists(encrypted_path):
        print(f"[!] Error: Encrypted image not found at {encrypted_path}")
        print("Please run main/run_crypto.py first.")
        sys.exit(1)
        
    # Load encrypted image to get dimensions
    enc_img = Image.open(encrypted_path).convert('L')
    enc_shape = enc_img.size
    enc_array = np.array(enc_img, dtype=np.uint8).flatten()
    
    # Load original image and resize to match encrypted image dimensions
    orig_array = load_image_as_array(original_path, size=enc_shape)
    
    print(f"Original Image Pixels Loaded: {len(orig_array)}")
    print(f"Encrypted Image Pixels Loaded: {len(enc_array)}")
    
    # Set up publication-style plot
    plt.figure(figsize=(12, 5))
    
    # Original Image Histogram
    plt.subplot(1, 2, 1)
    plt.hist(orig_array, bins=256, range=(0, 255), color='black', alpha=0.7)
    plt.title("Original Image Histogram", fontsize=14)
    plt.xlabel("Pixel Intensity", fontsize=12)
    plt.ylabel("Frequency", fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    
    # Encrypted Image Histogram
    plt.subplot(1, 2, 2)
    plt.hist(enc_array, bins=256, range=(0, 255), color='black', alpha=0.7)
    plt.title("Encrypted Image Histogram", fontsize=14)
    plt.xlabel("Pixel Intensity", fontsize=12)
    plt.ylabel("Frequency", fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    
    # Save figure
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"\n[*] Histogram generation successful.")
    print(f"Saved publication-quality figure to: {output_path}")
    print("======================================================")

if __name__ == "__main__":
    main()
