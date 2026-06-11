import numpy as np
import matplotlib.pyplot as plt

def plot_histogram_comparison(original_img, encrypted_img, decrypted_img, output_path):
    """
    Plots a comparison of the original, encrypted, and decrypted images along with
    their pixel intensity histograms.
    """
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    # 1. Plot Images
    axes[0, 0].imshow(original_img, cmap='gray')
    axes[0, 0].set_title("Original Image", fontsize=12)
    axes[0, 0].axis('off')
    
    axes[0, 1].imshow(encrypted_img, cmap='gray')
    axes[0, 1].set_title("Encrypted Image", fontsize=12)
    axes[0, 1].axis('off')
    
    axes[0, 2].imshow(decrypted_img, cmap='gray')
    axes[0, 2].set_title("Decrypted Image", fontsize=12)
    axes[0, 2].axis('off')
    
    # 2. Plot Histograms
    axes[1, 0].hist(original_img.ravel(), bins=256, range=(0, 256), color='blue', alpha=0.7)
    axes[1, 0].set_title("Original Histogram", fontsize=12)
    axes[1, 0].set_xlabel("Pixel Intensity")
    axes[1, 0].set_ylabel("Frequency")
    axes[1, 0].grid(True, linestyle='--', alpha=0.5)
    
    axes[1, 1].hist(encrypted_img.ravel(), bins=256, range=(0, 256), color='red', alpha=0.7)
    axes[1, 1].set_title("Encrypted Histogram", fontsize=12)
    axes[1, 1].set_xlabel("Pixel Intensity")
    axes[1, 1].set_ylabel("Frequency")
    axes[1, 1].grid(True, linestyle='--', alpha=0.5)
    
    axes[1, 2].hist(decrypted_img.ravel(), bins=256, range=(0, 256), color='green', alpha=0.7)
    axes[1, 2].set_title("Decrypted Histogram", fontsize=12)
    axes[1, 2].set_xlabel("Pixel Intensity")
    axes[1, 2].set_ylabel("Frequency")
    axes[1, 2].grid(True, linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved histogram analysis plot to {output_path}")
