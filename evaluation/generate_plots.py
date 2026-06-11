import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def main():
    base_dir = "/Users/archismanchoudhury/Desktop/research/Research Implementation"
    bench_csv = os.path.join(base_dir, "evaluation", "benchmark_results.csv")
    perf_csv = os.path.join(base_dir, "evaluation", "performance_results.csv")
    output_png = os.path.join(base_dir, "evaluation", "comparison_plots.png")
    
    if not os.path.exists(bench_csv) or not os.path.exists(perf_csv):
        print("[!] Error: Benchmark or performance CSV files not found. Run bench scripts first.")
        return
        
    df_bench = pd.read_csv(bench_csv)
    df_perf = pd.read_csv(perf_csv)
    
    # Set plot style for academic publication
    plt.rcParams.update({
        'font.size': 10,
        'axes.labelsize': 11,
        'axes.titlesize': 12,
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'figure.titlesize': 14,
        'font.family': 'sans-serif'
    })
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    images = df_bench["Image"].unique()
    x = np.arange(len(images))
    width = 0.35
    
    # 1. Shannon Entropy Comparison
    entropy_r = df_bench[df_bench["Mode"] == "robust"]["Entropy"].values
    entropy_p = df_bench[df_bench["Mode"] == "paper"]["Entropy"].values
    axes[0].bar(x - width/2, entropy_r, width, label='Robust Mode', color='#1f77b4', alpha=0.85)
    axes[0].bar(x + width/2, entropy_p, width, label='Paper Mode', color='#ff7f0e', alpha=0.85)
    axes[0].axhline(y=8.0, color='r', linestyle='--', label='Ideal (8.0)')
    axes[0].set_title("Shannon Entropy")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(images)
    axes[0].set_ylim(7.5, 8.05)
    axes[0].set_ylabel("Entropy (bits)")
    axes[0].legend(loc="lower right")
    axes[0].grid(True, linestyle=':', alpha=0.6)
    
    # 2. NPCR Comparison
    npcr_r = df_bench[df_bench["Mode"] == "robust"]["NPCR"].values
    npcr_p = df_bench[df_bench["Mode"] == "paper"]["NPCR"].values
    axes[1].bar(x - width/2, npcr_r, width, label='Robust Mode', color='#1f77b4', alpha=0.85)
    axes[1].bar(x + width/2, npcr_p, width, label='Paper Mode', color='#ff7f0e', alpha=0.85)
    axes[1].axhline(y=99.6, color='r', linestyle='--', label='Ideal (~99.6%)')
    axes[1].set_title("NPCR (%)")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(images)
    axes[1].set_ylim(99.0, 100.0)
    axes[1].set_ylabel("NPCR %")
    axes[1].legend(loc="lower right")
    axes[1].grid(True, linestyle=':', alpha=0.6)
    
    # 3. UACI Comparison
    uaci_r = df_bench[df_bench["Mode"] == "robust"]["UACI"].values
    uaci_p = df_bench[df_bench["Mode"] == "paper"]["UACI"].values
    axes[2].bar(x - width/2, uaci_r, width, label='Robust Mode', color='#1f77b4', alpha=0.85)
    axes[2].bar(x + width/2, uaci_p, width, label='Paper Mode', color='#ff7f0e', alpha=0.85)
    axes[2].axhline(y=33.46, color='r', linestyle='--', label='Ideal (~33.46%)')
    axes[2].set_title("UACI (%)")
    axes[2].set_xticks(x)
    axes[2].set_xticklabels(images)
    axes[2].set_ylim(30.0, 42.0)
    axes[2].set_ylabel("UACI %")
    axes[2].legend(loc="lower right")
    axes[2].grid(True, linestyle=':', alpha=0.6)
    
    # 4. Correlation Comparison (Average H, V, D)
    avg_corr_r = df_bench[df_bench["Mode"] == "robust"][["H_Corr", "V_Corr", "D_Corr"]].abs().mean(axis=1).values
    avg_corr_p = df_bench[df_bench["Mode"] == "paper"][["H_Corr", "V_Corr", "D_Corr"]].abs().mean(axis=1).values
    axes[3].bar(x - width/2, avg_corr_r, width, label='Robust Mode', color='#1f77b4', alpha=0.85)
    axes[3].bar(x + width/2, avg_corr_p, width, label='Paper Mode', color='#ff7f0e', alpha=0.85)
    axes[3].set_title("Mean Abs Adjacent Correlation")
    axes[3].set_xticks(x)
    axes[3].set_xticklabels(images)
    axes[3].set_ylabel("Correlation (r)")
    axes[3].legend()
    axes[3].grid(True, linestyle=':', alpha=0.6)
    
    # 5. Throughput Comparison
    modes = df_perf["Mode"].unique()
    throughput_enc = df_perf["Encryption_Throughput_MBs"].values
    throughput_dec = df_perf["Decryption_Throughput_MBs"].values
    x_perf = np.arange(len(modes))
    
    axes[4].bar(x_perf - width/2, throughput_enc, width, label='Encryption', color='#2ca02c', alpha=0.85)
    axes[4].bar(x_perf + width/2, throughput_dec, width, label='Decryption', color='#d62728', alpha=0.85)
    axes[4].set_title("Throughput Comparison")
    axes[4].set_xticks(x_perf)
    axes[4].set_xticklabels(["Robust Mode", "Paper Mode"])
    axes[4].set_ylabel("Throughput (MB/s)")
    axes[4].legend()
    axes[4].grid(True, linestyle=':', alpha=0.6)
    
    # 6. Peak Memory Usage Comparison
    peak_mem = df_perf["Peak_Process_Memory_MB"].values
    axes[5].bar(x_perf, peak_mem, width, color=['#1f77b4', '#ff7f0e'], alpha=0.85)
    axes[5].set_title("Peak Process Memory Usage")
    axes[5].set_xticks(x_perf)
    axes[5].set_xticklabels(["Robust Mode", "Paper Mode"])
    axes[5].set_ylabel("Memory (MB)")
    axes[5].grid(True, linestyle=':', alpha=0.6)
    
    fig.suptitle("Fractional-Order Secure Communication System Benchmark Comparison", fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_png, dpi=300)
    plt.close()
    print(f"[+] Saved comparison plots to {output_png}")

if __name__ == "__main__":
    main()
