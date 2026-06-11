import numpy as np
from paper_mode.direct_key_extractor import extract_paper_keys

def encrypt_paper(image_bytes, states):
    """
    Encrypts an image using global permutation followed by non-linear
    forward and backward diffusion modulo 256.
    
    Both permutation indices and diffusion keys are derived directly
    from synchronized chaotic trajectories without SHA-256 or PRNG.
    """
    N = len(image_bytes)
    
    # Extract keys directly from trajectories
    keys = extract_paper_keys(states)
    
    # 1. Global Permutation using state keys[:, 0]
    # We use kind='stable' to ensure that if key values are identical,
    # their relative order is deterministic and noise-immune.
    perm_indices = np.argsort(keys[:N, 0], kind='stable')
    permuted_bytes = image_bytes[perm_indices].astype(np.int32)
    
    # 2. Diffusion using state keys[:, 3]
    k = keys[:N, 3].astype(np.int32)
    
    # Forward diffusion
    c_forward = np.zeros(N, dtype=np.int32)
    curr = 0
    for i in range(N):
        curr = (permuted_bytes[i] + k[i] + curr) % 256
        c_forward[i] = curr
        
    # Backward diffusion
    c_backward = np.zeros(N, dtype=np.int32)
    curr = 0
    for i in range(N - 1, -1, -1):
        curr = (c_forward[i] + k[i] + curr) % 256
        c_backward[i] = curr
        
    return c_backward.astype(np.uint8)
