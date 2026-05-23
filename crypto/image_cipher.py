import numpy as np

def encrypt_image(image_bytes, keys):
    """
    Encrypts an image using permutation and XOR diffusion.
    keys: array of shape (N, 6) containing uint8 keys extracted from states.
    N must be >= len(image_bytes).
    """
    N = len(image_bytes)
    
    # 1. Permutation using x1 (keys[:, 0])
    perm_indices = np.argsort(keys[:N, 0])
    permuted_bytes = image_bytes[perm_indices]
    
    # 2. Diffusion using x4 (keys[:, 3])
    cipher_bytes = np.bitwise_xor(permuted_bytes, keys[:N, 3])
    
    return cipher_bytes

def decrypt_image(cipher_bytes, keys):
    """
    Decrypts the image by reversing diffusion then permutation.
    """
    N = len(cipher_bytes)
    
    # 1. Reverse Diffusion using x4
    permuted_bytes = np.bitwise_xor(cipher_bytes, keys[:N, 3])
    
    # 2. Reverse Permutation using x1
    perm_indices = np.argsort(keys[:N, 0])
    
    # We need to invert the permutation indices
    inv_perm_indices = np.empty_like(perm_indices)
    inv_perm_indices[perm_indices] = np.arange(N)
    
    decrypted_bytes = permuted_bytes[inv_perm_indices]
    
    return decrypted_bytes
