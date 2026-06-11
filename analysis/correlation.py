import numpy as np
import matplotlib.pyplot as plt

def get_adjacent_pairs(img, direction, num_samples=5000):
    """
    Randomly samples adjacent pixel pairs in the specified direction
    and computes the Pearson correlation coefficient.
    """
    H, W = img.shape
    
    if direction == 'horizontal':
        max_h, max_w = H, W - 1
        offset_h, offset_w = 0, 1
    elif direction == 'vertical':
        max_h, max_w = H - 1, W
        offset_h, offset_w = 1, 0
    elif direction == 'diagonal':
        max_h, max_w = H - 1, W - 1
        offset_h, offset_w = 1, 1
    else:
        raise ValueError("Invalid direction. Use 'horizontal', 'vertical', or 'diagonal'.")
        
    # Vectorized random sampling of indices
    idx_h = np.random.randint(0, max_h, num_samples)
    idx_w = np.random.randint(0, max_w, num_samples)
    
    pixels_1 = img[idx_h, idx_w].astype(np.float64)
    pixels_2 = img[idx_h + offset_h, idx_w + offset_w].astype(np.float64)
    
    # Calculate Pearson correlation coefficient
    corr_matrix = np.corrcoef(pixels_1, pixels_2)
    # Check for constant arrays (prevent NaN)
    if np.isnan(corr_matrix).any():
        corr_coeff = 0.0
    else:
        corr_coeff = corr_matrix[0, 1]
        
    return pixels_1, pixels_2, corr_coeff

def plot_correlation_scatter(original_img, encrypted_img, direction, output_path, num_samples=5000):
    """
    Generates side-by-side scatter plots for original and encrypted images in a given direction.
    """
    x_orig, y_orig, r_orig = get_adjacent_pairs(original_img, direction, num_samples)
    x_enc, y_enc, r_enc = get_adjacent_pairs(encrypted_img, direction, num_samples)
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))
    
    # Original scatter plot
    axes[0].scatter(x_orig, y_orig, s=1, color='blue', alpha=0.5)
    axes[0].set_title(f"Original Image (r = {r_orig:.4f})", fontsize=12)
    axes[0].set_xlabel("Pixel Value at (x, y)")
    axes[0].set_ylabel("Pixel Value at Neighbor")
    axes[0].set_xlim(0, 255)
    axes[0].set_ylim(0, 255)
    axes[0].grid(True, linestyle='--', alpha=0.5)
    
    # Encrypted scatter plot
    axes[1].scatter(x_enc, y_enc, s=1, color='red', alpha=0.5)
    axes[1].set_title(f"Encrypted Image (r = {r_enc:.4f})", fontsize=12)
    axes[1].set_xlabel("Pixel Value at (x, y)")
    axes[1].set_ylabel("Pixel Value at Neighbor")
    axes[1].set_xlim(0, 255)
    axes[1].set_ylim(0, 255)
    axes[1].grid(True, linestyle='--', alpha=0.5)
    
    fig.suptitle(f"{direction.capitalize()} Adjacent Pixel Correlation", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Saved {direction} correlation scatter plot to {output_path}")
    return r_orig, r_enc

def run_correlation_analysis(original_img, encrypted_img, report_path, plots_dir):
    """
    Runs correlation analysis for all directions, saves scatter plots, and writes a report.
    """
    directions = ['horizontal', 'vertical', 'diagonal']
    results = {}
    
    for d in directions:
        plot_path = f"{plots_dir}/correlation_{d}.png"
        r_orig, r_enc = plot_correlation_scatter(original_img, encrypted_img, d, plot_path)
        results[d] = (r_orig, r_enc)
        
    with open(report_path, 'w') as f:
        f.write("=== ADJACENT PIXEL CORRELATION ANALYSIS REPORT ===\n\n")
        f.write("Original Correlation:\n")
        for d in directions:
            f.write(f"{d.capitalize():12} = {results[d][0]:.6f}\n")
        f.write("\nEncrypted Correlation:\n")
        for d in directions:
            f.write(f"{d.capitalize():12} = {results[d][1]:.6f}\n")
            
    print(f"Saved correlation report to {report_path}")
    return results
