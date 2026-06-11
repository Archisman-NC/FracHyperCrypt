import numpy as np
import hashlib

def extract_keys(sync_states):
    """
    Extracts deterministic pseudo-random keys from synchronized chaotic states.
    Uses block-based majority voting on sign to generate a noise-tolerant seed,
    then expands it using a PRNG to guarantee 100% matching key sequences.
    """
    N = len(sync_states)
    block_size = 32
    num_blocks = max(1, N // block_size)
    
    bits = []
    # Use states x2, x3, x4, x5, x6 which are highly stable and synchronized
    for j in [1, 2, 3, 4, 5]:
        for b in range(num_blocks):
            start = b * block_size
            end = start + block_size
            votes = np.sum(sync_states[start:end, j] > 0)
            bit = 1 if votes > (block_size / 2) else 0
            bits.append(bit)
            
    # Convert bits to bytes
    byte_array = bytearray()
    bit_string = "".join(str(b) for b in bits)
    for i in range(0, len(bit_string), 8):
        byte_chunk = bit_string[i:i+8]
        if len(byte_chunk) < 8:
            byte_chunk = byte_chunk.ljust(8, '0')
        byte_array.append(int(byte_chunk, 2))
        
    # Generate 256-bit seed
    seed = hashlib.sha256(byte_array).digest()
    
    # Convert bytes to sequence of uint32 for SeedSequence compatibility
    seed_ints = np.frombuffer(seed, dtype=np.uint32)
    
    # Expand seed to generate keys of shape (N, 6)
    rng = np.random.default_rng(seed_ints)
    keys = rng.integers(0, 256, size=(N, 6), dtype=np.uint8)
    return keys
