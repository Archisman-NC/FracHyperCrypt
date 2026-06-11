import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_block(ax, text, xy, width, height, bg_color='#34495e', border_color='#2c3e50'):
    """Draws a styled rectangular box for flowchart steps."""
    rect = patches.FancyBboxPatch(
        xy, width, height,
        boxstyle="round,pad=0.08",
        facecolor=bg_color,
        edgecolor=border_color,
        linewidth=1.5,
        alpha=0.9
    )
    ax.add_patch(rect)
    # Put text inside
    ax.text(
        xy[0] + width/2, xy[1] + height/2,
        text,
        color='white',
        fontsize=9,
        fontweight='bold',
        ha='center',
        va='center',
        multialignment='center'
    )

def draw_arrow(ax, start, end, label=""):
    """Draws a directed connection line between blocks."""
    ax.annotate(
        label,
        xy=end,
        xytext=start,
        arrowprops=dict(facecolor='#2c3e50', edgecolor='#2c3e50', width=1.5, headwidth=6, shrink=0.05),
        fontsize=8,
        color='#34495e',
        ha='center',
        va='bottom'
    )

def main():
    base_dir = "/Users/archismanchoudhury/Desktop/research/Research Implementation"
    output_png = os.path.join(base_dir, "docs", "Architecture.png")
    
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Title
    ax.text(6, 7.6, "System Architecture: Projective Sliding Mode Synchronization & Dual-Mode Cryptography",
            fontsize=13, fontweight='bold', ha='center', color='#2c3e50')
    
    # ------------------ TRANSMITTER (DRIVE SYSTEM) ------------------
    ax.text(1.5, 7.1, "TRANSMITTER (DRIVE SIDE)", fontsize=10, fontweight='bold', color='#1f77b4')
    # Draw border around Transmitter
    rect_tx = patches.Rectangle((0.2, 2.5), 5.4, 4.3, linewidth=1, edgecolor='#b4c6e7', facecolor='#f2f5f9', linestyle='--')
    ax.add_patch(rect_tx)
    
    draw_block(ax, "6D Fractional\nDrive System\n(x1...x6)", (0.5, 5.5), 1.8, 0.8, bg_color='#1f77b4')
    draw_arrow(ax, (1.4, 5.5), (1.4, 4.3))
    draw_block(ax, "Fractional Solver\n(ABM-PC Engine)", (0.5, 3.5), 1.8, 0.8, bg_color='#2ca02c')
    
    # Mode branches (Transmitter)
    ax.text(3.8, 6.2, "DUAL-MODE CRYPTOGRAPHY", fontsize=8, fontweight='bold', color='#7f7f7f', ha='center')
    draw_arrow(ax, (2.3, 3.9), (3.0, 5.0), label="Paper Mode")
    draw_arrow(ax, (2.3, 3.9), (3.0, 3.0), label="Robust Mode")
    
    # Paper Mode Keygen Box
    draw_block(ax, "Direct Coarse\nQuantization\n(x1,x3,x5,x6)", (3.0, 4.8), 2.2, 0.8, bg_color='#d62728')
    # Robust Mode Keygen Box
    draw_block(ax, "Majority Vote\n+ SHA-256 + PRNG", (3.0, 2.8), 2.2, 0.8, bg_color='#9467bd')
    
    # Conjoin to encryption
    draw_arrow(ax, (5.2, 5.2), (5.5, 4.5))
    draw_arrow(ax, (5.2, 3.2), (5.5, 4.1))
    draw_block(ax, "Image Encryption\n(Permute + Diffuse)", (5.5, 3.8), 2.0, 0.8, bg_color='#e377c2')
    
    # ------------------ TRANSMISSION CHANNEL ------------------
    ax.text(6.1, 2.1, "PHYSICAL CHANNEL", fontsize=9, fontweight='bold', color='#e377c2', ha='center')
    rect_chan = patches.Rectangle((5.7, 0.5), 0.8, 1.8, linewidth=1, edgecolor='#ffc7ce', facecolor='#ffebec')
    ax.add_patch(rect_chan)
    ax.text(6.1, 1.4, "Ciphertext\nImage", fontsize=8, ha='center', color='#9c0006')
    
    # Arrows to/from Channel
    draw_arrow(ax, (6.5, 3.8), (6.1, 2.3)) # Ciphertext to channel
    draw_arrow(ax, (1.4, 3.5), (6.1, 0.5), label="Drive Signal x1(t)") # Transmitted x1
    
    # ------------------ RECEIVER (RESPONSE SIDE) ------------------
    ax.text(10.5, 7.1, "RECEIVER (RESPONSE SIDE)", fontsize=10, fontweight='bold', color='#ff7f0e', ha='right')
    rect_rx = patches.Rectangle((6.4, 2.5), 5.4, 4.3, linewidth=1, edgecolor='#ffd8b1', facecolor='#fffbf7', linestyle='--')
    ax.add_patch(rect_rx)
    
    draw_block(ax, "SMC Controller &\nNonlinear Cancellation", (6.6, 5.5), 2.1, 0.8, bg_color='#ff7f0e')
    # Input x1 to controller
    draw_arrow(ax, (6.1, 0.5), (7.6, 5.5), label="SMC Feedback")
    
    draw_arrow(ax, (8.7, 5.9), (9.5, 5.9))
    draw_block(ax, "6D Fractional\nResponse System\n(y1...y6) + ABM", (9.5, 5.5), 2.1, 0.8, bg_color='#2ca02c')
    
    # Mode branches (Receiver)
    draw_arrow(ax, (10.5, 5.5), (9.8, 4.3), label="Paper Mode")
    draw_arrow(ax, (10.5, 5.5), (9.8, 2.7), label="Robust Mode")
    
    # Key Recovery Boxes
    draw_block(ax, "Direct Trajectory\nQuantization", (8.0, 3.8), 1.8, 0.7, bg_color='#d62728')
    draw_block(ax, "Majority Vote\n+ SHA-256 + PRNG", (8.0, 2.6), 1.8, 0.7, bg_color='#9467bd')
    
    # Decryption
    draw_arrow(ax, (8.0, 3.8), (7.5, 3.5))
    draw_arrow(ax, (8.0, 2.6), (7.5, 3.1))
    draw_block(ax, "Image Decryption\n(Inv Diff + Inv Perm)", (7.5, 3.1), 2.0, 0.8, bg_color='#e377c2')
    
    # Decrypted Plaintext output
    draw_arrow(ax, (6.1, 2.3), (7.5, 3.5)) # ciphertext from channel
    draw_arrow(ax, (8.5, 3.1), (9.5, 3.5))
    draw_block(ax, "Recovered\nPlaintext Image", (9.5, 3.1), 2.0, 0.8, bg_color='#34495e')
    
    # Save diagram
    plt.savefig(output_png, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[+] Saved publication-quality architecture diagram to {output_png}")

if __name__ == "__main__":
    main()
