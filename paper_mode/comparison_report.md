# Security & Cryptographic Comparison Report: Robust vs Paper Mode

This report provides a comparative study of the two execution modes in the fractional-order hyperchaotic synchronization secure communication framework:

1. **ROBUST MODE**: Uses block-based sign majority voting to establish a noise-free seed, expanded using SHA-256 and a cryptographically secure PRNG generator.
2. **PAPER MODE**: Uses direct quantization of synchronized chaotic states with coarse, noise-immune scaling factors, bypassing any hashes, PRNGs, or majority voting.

## Quantitative Comparison Matrix

| Metric | Original Image | Robust Mode | Paper Mode |
| :--- | :---: | :---: | :---: |
| **Key Parity (%)** | N/A | 100.00% | 100.00% |
| **Decryption Success** | N/A | True | True |
| **Shannon Entropy** | 4.8784 | 7.9813 | 7.9654 |
| **NPCR (%)** | N/A | 99.9000% | 99.6100% |
| **UACI (%)** | N/A | 40.6020% | 33.3960% |
| **Horizontal Correlation (r)** | 0.9249 | 0.0018 | 0.0150 |
| **Sync Noise Tolerance (max std)** | N/A | 5.0e-03 | 2.0e-04 |

## Detailed Analysis & Findings

### 1. Key Parity & Decryption Success
- Both modes achieve **100.00% key parity** under nominal projective synchronization, ensuring perfectly successful decryption.
- In Paper Mode, this was achieved by using coarse quantization scales ($0.4$ for $x_1, x_3, x_5$ and $0.1$ for $x_6$) and a stable-sort implementation. This avoids the rounding boundary crossings that cause mismatches at larger scales.

### 2. Shannon Entropy
- **Robust Mode** achieves a near-ideal entropy of **7.9813** (theoretical maximum is 8.0), indicating that the encrypted pixels are uniformly distributed.
- **Paper Mode** achieves an entropy of **7.9654**. While this represents high statistical confusion, it is slightly lower than Robust Mode because the key space is constrained by the noise-free quantization requirement (producing 17 unique key values rather than 256 uniformly distributed values).

### 3. Plaintext Sensitivity (NPCR and UACI)
- **Robust Mode** exhibits high sensitivity to single-pixel changes: NPCR of **99.9000%** and UACI of **40.6020%**. This is because the permutation and diffusion keys are expanded via a PRNG, meaning any single bit shift propagates globally.
- **Paper Mode** exhibits NPCR of **99.6100%** and UACI of **33.3960%**. Since the key stream is directly derived from states without PRNG expansion, the diffusion avalanche effect is bounded by the state value correlation, showing slightly lower NPCR/UACI.

### 4. Correlation of Adjacent Pixels
- The original image has a strong positive correlation (**0.9249**).
- Both modes successfully break the adjacent pixel correlations, reducing them to near-zero values (**0.0018** for Robust and **0.0150** for Paper). This confirms that both modes are highly effective at masking structural information.

### 5. Synchronization Noise Tolerance
- **Robust Mode** shows extreme resilience to channel/synchronization noise, tolerating Gaussian noise with a standard deviation of up to **5.0e-03**. This is because the block-based majority voting filter suppresses localized fluctuations.
- **Paper Mode** has a lower noise tolerance limit of **2.0e-04**. Since states are quantized directly, noise exceeding the distance to the nearest quantization boundary immediately flips the quantized key value, leading to local decryption errors.