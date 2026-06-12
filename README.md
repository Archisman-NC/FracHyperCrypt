# Fractional-Order Hyperchaotic Synchronization for Secure Communication

This repository contains a research-grade Python implementation of finite-time projective synchronization of a 6D fractional-order hyperchaotic system via sliding mode control. It applies this synchronization technique to secure image encryption and decryption.

The implementation focuses on numerical precision, execution speed, and mathematical faithfulness using the Fractional Adams-Bashforth-Moulton Predictor-Corrector (ABM-PC) solver combined with epsilon-regularized nonlinear control.

## System Architecture

```text
/fractional_core
    ├── abm_solver.py         # Fractional ABM-PC Predictor-Corrector Engine
/chaos
    ├── drive_system.py       # 6D Hyperchaotic Transmitter Dynamics
    ├── response_system.py    # 6D Hyperchaotic Receiver Dynamics
/sync
    ├── integrator.py         # Finite-memory fractional integrator
    ├── sliding_surface.py    # Fractional sliding surface computation
    ├── controller.py         # Epsilon-regularized nonlinear control law
    ├── synchronizer.py       # Cancellation term computation
/crypto
    ├── key_extractor.py      # Mantissa layer extraction for cryptography
    ├── image_cipher.py       # XOR Diffusion and Permutation
/main
    ├── run_attractor.py      # Attractor visualization execution
    ├── run_sync.py           # Explicit synchronization orchestration
```

## Setup Instructions

Ensure you have Python 3.8+ installed. Install the minimal scientific computing stack:

```bash
pip install -r requirements.txt
```

Parameters for the fractional order, solvers, integration time, and control gains are fully centralized in `config.py`.

## Execution Order

Run the scripts from the root repository directory to observe the pipeline:

### 1. Attractor Generation
Validates the fractional order $q$ and solver memory truncation lengths ($L$) by generating stable hyperchaotic phase portraits.
```bash
python main/run_attractor.py
```

### 2. Synchronization Loop
Executes the causal explicit synchronization loop, computing control efforts and capturing the error state reduction.
```bash
python main/run_sync.py
```

### 3. Image Encryption / Decryption Pipeline
Encrypts and decrypts the standard test image using the active mode.
```bash
python main/run_crypto.py
```

## Testing with Your Own Images

You can encrypt and decrypt any custom image (JPG, PNG, BMP, etc.) using the CLI utility:

```bash
python main/encrypt_custom.py -i <path_to_image> -m <robust|paper> -s <pixel_dimension>
```

### Example Usage:
```bash
python main/encrypt_custom.py -i images/lena.png -m robust -s 128
```

### Options:
* `-i`, `--image`: (Required) Path to the custom image file.
* `-m`, `--mode`: (Optional) Keystream derivation mode: `'robust'` (SHA-256 + LCG, default) or `'paper'` (Direct Quantization).
* `-s`, `--size`: (Optional) Resizes the image to `size x size` pixels to keep the fractional synchronization simulation time fast (default: `256`).

## Generated Outputs
Outputs are saved in the `results/` directory:
* `results/attractor.png` - Phase portraits of the fractional system.
* `results/sync_errors.png` - Validation of projective synchronization.
* `results/encrypted.png`, `results/decrypted.png`, `results/comparison.png` - Outputs from the default run.
* `results/custom_encrypted.png`, `results/custom_decrypted.png`, `results/custom_comparison.png` - Outputs from custom image test runs.

## Implementation Details
For a deep dive into the mathematical decisions, including the Short-Memory Principle truncation and the treatment of explicit $O(h)$ causal lag, refer to the `docs/walkthrough.md` generated during development.

