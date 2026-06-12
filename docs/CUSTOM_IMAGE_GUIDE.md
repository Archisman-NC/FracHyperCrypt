# Custom Image Encryption Guide

This guide provides step-by-step instructions on setting up the environment, running the encryption pipeline with your own custom images, and interpreting the statistical analysis reports.

---

## 1. Environment Setup

Ensure you have Python 3.8 or newer installed on your system.

### Install Dependencies
Clone the repository and install the minimal scientific computing stack using `pip`:

```bash
pip install -r requirements.txt
```

*Note: The core dependencies are `numpy`, `scipy`, `matplotlib`, and `pillow` (PIL).*

---

## 2. Running the Encryption with Custom Images

We provide an interactive CLI tool (`main/encrypt_custom.py`) to easily test the fractional sliding mode synchronization encryption and decryption cycle with any image file (PNG, JPG, BMP, etc.).

### Command Syntax

```bash
python main/encrypt_custom.py -i <path_to_image> [options]
```

### Options and Parameters

| Option | Flag | Description | Default | Recommended |
| :--- | :--- | :--- | :--- | :--- |
| `--image` | `-i` | **(Required)** Path to your custom image file. | N/A | Direct absolute or relative path |
| `--mode` | `-m` | Keystream derivation mode: `robust` or `paper`. | `robust` | `robust` (higher security, noise-filtered) |
| `--size` | `-s` | Pixel dimensions to resize the image (`size x size`). | `256` | `128` (fast simulation) or `256` (standard) |

### Example Commands

#### A. Fast Demo (Robust Mode, 128x128 resolution)
Resizes your image to $128 \times 128$ grayscale pixels. The fractional-order solver will run in approximately 4–6 seconds.
```bash
python main/encrypt_custom.py -i path/to/your_photo.jpg -m robust -s 128
```

#### B. Full Resolution Demo (Robust Mode, 256x256 resolution)
Resizes your image to $256 \times 256$ grayscale pixels. The fractional solver will run in approximately 18–25 seconds.
```bash
python main/encrypt_custom.py -i path/to/your_photo.png -m robust -s 256
```

#### C. Paper Mode Demo (Direct Trajectory Quantization, 128x128)
Tests the direct state quantization mode without SHA-256 or LCG PRNG seed expansion.
```bash
python main/encrypt_custom.py -i path/to/your_photo.jpg -m paper -s 128
```

---

## 3. Locating and Understanding the Outputs

After running the script, three visualization files are generated in the `results/` folder:

```text
/results
    ├── custom_encrypted.png    # The encrypted ciphertext (visual noise)
    ├── custom_decrypted.png    # The decrypted output image
    └── custom_comparison.png   # Side-by-side: Plaintext, Ciphertext, Decrypted
```

### Decoding the Terminal Report
At the end of the execution, the script prints a **Security & Performance Summary Table**:

```text
============================================================
    SECURITY & PERFORMANCE EVALUATION SUMMARY
============================================================
Decryption Integrity Status  : SUCCESS (100% Bit-Identical)
Original Image Entropy       : 7.411977 bits
Encrypted Image Entropy      : 7.990385 bits (Target: >7.99)
Horizontal Pixel Correlation : -0.006701
Vertical Pixel Correlation   : 0.017125
Diagonal Pixel Correlation   : -0.016334
Encryption Time              : 0.0082 seconds
Decryption Time              : 0.0106 seconds
Total Simulation & Run Time  : 5.75 seconds
============================================================
```

#### How to read the metrics:
1. **Decryption Integrity Status**: Must show `SUCCESS (100% Bit-Identical)`. This guarantees that the receiver successfully synchronized with the transmitter in finite time, extracted matching keys, and reversed the pixel permutation and diffusion without a single pixel error.
2. **Encrypted Image Entropy**: Measures pixel randomness. The maximum entropy for an 8-bit grayscale image is `8.0000`. 
   * **Robust Mode** should achieve $>7.99$ (ideal information security).
   * **Paper Mode** will typically show slightly lower entropy ($7.96$ to $7.97$) due to the entropy deficit caused by direct coarse quantization.
3. **Pixel Correlation Coefficients (Horizontal/Vertical/Diagonal)**: Measures spatial redundancy. 
   * In normal images, adjacent pixels are highly correlated (close to `1.0`). 
   * In a secure ciphertext, these values must drop close to `0.0` (typically $< 0.02$), signifying that all spatial redundancy has been successfully broken, protecting the image against statistical cryptanalysis.

---

## 4. Advanced: Tweaking System Dynamics

You can customize the fractional-order system parameters directly in the central config file, [config.py](file:///Users/archismanchoudhury/Desktop/research/Research%20Implementation/config.py):

* **Fractional Order ($q$)**: Modify `Q` (default `0.8`). You can test orders like `0.9` or `0.75` to observe fractional dynamic memory impacts.
* **Synchronization Gains ($\alpha, \beta$)**: Modify `ALPHA` and `BETA` to alter the sliding surface slope. Increasing these speeds up synchronization convergence, while decreasing them results in slower lock times.
* **Quantization Scaling**: For `paper` mode, the scaling factors in `paper_mode/direct_key_extractor.py` determine how finely or coarsely the chaotic attractors are sliced. Feel free to tweak them to study the synchronization noise boundaries.
