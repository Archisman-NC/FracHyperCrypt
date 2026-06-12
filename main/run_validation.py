import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from fractional_core.generator import generate_fractional_sequences

def main():
    print("=== Fractional-Order Validation (Diethelm ABM-PC) ===")
    
    # Generate q = 0.8 trajectories
    length = 5000
    print(f"Generating fractional trajectories (q={config.Q})...")
    traj_q08 = generate_fractional_sequences(length, discard_transients=True)
    
    # Generate q = 1.0 trajectories for comparison
    print("Generating integer-order trajectories (q=1.0) for comparison...")
    original_q = config.Q
    config.Q = 1.0
    traj_q10 = generate_fractional_sequences(length, discard_transients=True)
    config.Q = original_q # restore
    
    # Plotting State Trajectories
    plt.figure(figsize=(15, 8))
    
    plt.subplot(2, 1, 1)
    plt.plot(traj_q08[:, 0], label="x1 (q=0.8)", lw=1)
    plt.plot(traj_q08[:, 1], label="x2 (q=0.8)", lw=1)
    plt.plot(traj_q08[:, 2], label="x3 (q=0.8)", lw=1)
    plt.title("Fractional-Order State Trajectories (q=0.8)", fontsize=14)
    plt.legend(loc="upper right")
    plt.grid(True)
    
    plt.subplot(2, 1, 2)
    plt.plot(traj_q10[:, 0], label="x1 (q=1.0)", lw=1, alpha=0.7)
    plt.plot(traj_q10[:, 1], label="x2 (q=1.0)", lw=1, alpha=0.7)
    plt.plot(traj_q10[:, 2], label="x3 (q=1.0)", lw=1, alpha=0.7)
    plt.title("Integer-Order State Trajectories (q=1.0)", fontsize=14)
    plt.legend(loc="upper right")
    plt.grid(True)
    
    traj_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'results', 'trajectories_comparison.png')
    plt.tight_layout()
    plt.savefig(traj_path, dpi=300)
    plt.close()
    print(f"Saved trajectories comparison to {traj_path}")

    
    # Plotting Phase Portraits
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    # Phase portraits for q = 0.8
    axes[0, 0].plot(traj_q08[:, 0], traj_q08[:, 1], lw=0.5, color='blue')
    axes[0, 0].set_title('x1-x2 Phase Portrait (q=0.8)')
    axes[0, 0].set_xlabel('x1')
    axes[0, 0].set_ylabel('x2')
    
    axes[0, 1].plot(traj_q08[:, 1], traj_q08[:, 2], lw=0.5, color='blue')
    axes[0, 1].set_title('x2-x3 Phase Portrait (q=0.8)')
    axes[0, 1].set_xlabel('x2')
    axes[0, 1].set_ylabel('x3')
    
    axes[0, 2].plot(traj_q08[:, 0], traj_q08[:, 3], lw=0.5, color='blue')
    axes[0, 2].set_title('x1-x4 Phase Portrait (q=0.8)')
    axes[0, 2].set_xlabel('x1')
    axes[0, 2].set_ylabel('x4')
    
    # Phase portraits for q = 1.0
    axes[1, 0].plot(traj_q10[:, 0], traj_q10[:, 1], lw=0.5, color='red')
    axes[1, 0].set_title('x1-x2 Phase Portrait (q=1.0)')
    axes[1, 0].set_xlabel('x1')
    axes[1, 0].set_ylabel('x2')
    
    axes[1, 1].plot(traj_q10[:, 1], traj_q10[:, 2], lw=0.5, color='red')
    axes[1, 1].set_title('x2-x3 Phase Portrait (q=1.0)')
    axes[1, 1].set_xlabel('x2')
    axes[1, 1].set_ylabel('x3')
    
    axes[1, 2].plot(traj_q10[:, 0], traj_q10[:, 3], lw=0.5, color='red')
    axes[1, 2].set_title('x1-x4 Phase Portrait (q=1.0)')
    axes[1, 2].set_xlabel('x1')
    axes[1, 2].set_ylabel('x4')
    
    plt.tight_layout()
    phase_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'results', 'phase_portraits_comparison.png')
    plt.savefig(phase_path, dpi=300)
    plt.close()
    print(f"Saved phase portraits comparison to {phase_path}")

    
    print("=== Validation Complete ===")

if __name__ == "__main__":
    main()
