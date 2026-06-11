import numpy as np
from paper_mode.direct_key_extractor import extract_paper_keys

def decrypt_paper(cipher_bytes, states):
    """
    Decrypts the image by reversing the backward and forward diffusion,
    then inverting the permutation.
    
    All key sequences and permutation indices are derived directly
    from the synchronized response trajectories.
    """
    N = len(cipher_bytes)
    
    # Extract keys directly from trajectories
    keys = extract_paper_keys(states)
    k = keys[:N, 3].astype(np.int32)
    c_backward = cipher_bytes.astype(np.int32)
    
    # 1. Reverse Backward Diffusion
    c_forward = np.zeros(N, dtype=np.int32)
    for i in range(N):
        if i == N - 1:
            c_forward[i] = (c_backward[i] - k[i] - 0) % 256
        else:
            c_forward[i] = (c_backward[i] - k[i] - c_backward[i+1]) % 256
            
    # 2. Reverse Forward Diffusion
    permuted_bytes = np.zeros(N, dtype=np.int32)
    for i in range(N):
        if i == 0:
            permuted_bytes[i] = (c_forward[i] - k[i] - 0) % 256
        else:
            permuted_bytes[i] = (c_forward[i] - k[i] - c_forward[i-1]) % 256
            
    # 3. Reverse Permutation
    perm_indices = np.argsort(keys[:N, 0], kind='stable')
    inv_perm_indices = np.empty_like(perm_indices)
    inv_perm_indices[perm_indices] = np.arange(N)
    decrypted_bytes = permuted_bytes[inv_perm_indices].astype(np.uint8)
    
    return decrypted_bytes
