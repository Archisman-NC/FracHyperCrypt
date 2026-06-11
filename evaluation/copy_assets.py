import os
import shutil
import pandas as pd

def main():
    base_dir = "/Users/archismanchoudhury/Desktop/research/Research Implementation"
    docs_dir = os.path.join(base_dir, "docs")
    results_out_dir = os.path.join(docs_dir, "Results")
    
    # Create directories
    os.makedirs(docs_dir, exist_ok=True)
    os.makedirs(results_out_dir, exist_ok=True)
    print(f"[*] Created directories: {docs_dir} and {results_out_dir}")
    
    # 1. Format and copy Benchmark_Tables.csv
    src_csv = os.path.join(base_dir, "evaluation", "benchmark_results.csv")
    dest_csv = os.path.join(docs_dir, "Benchmark_Tables.csv")
    
    if os.path.exists(src_csv):
        print(f"[*] Formatting {src_csv} into {dest_csv}...")
        df = pd.read_csv(src_csv)
        
        # Select and rename columns as requested
        column_mapping = {
            "Image": "Image",
            "Mode": "Mode",
            "Entropy": "Entropy",
            "NPCR": "NPCR",
            "UACI": "UACI",
            "H_Corr": "Horizontal Correlation",
            "V_Corr": "Vertical Correlation",
            "D_Corr": "Diagonal Correlation",
            "Enc_Time": "Encryption Time",
            "Dec_Time": "Decryption Time"
        }
        
        # Filter and rename
        df_filtered = df[list(column_mapping.keys())].rename(columns=column_mapping)
        df_filtered.to_csv(dest_csv, index=False)
        print(f"[+] Saved formatted benchmark tables to {dest_csv}")
    else:
        print(f"[!] Error: Source CSV not found at {src_csv}")
        
    # 2. Copy result images
    image_mappings = {
        "results/trajectories_comparison.png": "docs/Results/trajectories.png",
        "results/phase_portraits_comparison.png": "docs/Results/phase_portraits.png",
        "results/sync_errors.png": "docs/Results/synchronization_error.png",
        "results/histogram.png": "docs/Results/histogram.png",
        "results/correlation_horizontal.png": "docs/Results/correlation_horizontal.png",
        "results/correlation_vertical.png": "docs/Results/correlation_vertical.png",
        "results/correlation_diagonal.png": "docs/Results/correlation_diagonal.png",
        "results/key_sensitivity.png": "docs/Results/key_sensitivity.png",
        "evaluation/comparison_plots.png": "docs/Results/comparison_plots.png"
    }
    
    print("\n[*] Copying results images to docs/Results/...")
    for src_rel, dest_rel in image_mappings.items():
        src_path = os.path.join(base_dir, src_rel)
        dest_path = os.path.join(base_dir, dest_rel)
        
        if os.path.exists(src_path):
            shutil.copy2(src_path, dest_path)
            print(f"  [+] Copied {src_rel} -> {dest_rel}")
        else:
            print(f"  [!] Warning: Source file not found: {src_path}")
            
    print("\n[+] Asset copy and formatting completed successfully.")

if __name__ == "__main__":
    main()
