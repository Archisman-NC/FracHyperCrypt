import numpy as np

def extract_keys(sync_states):
    """
    Extracts deterministic pseudo-random bytes from synchronized chaotic states.
    Because of the O(h) integration error lag (approx 1e-3), extracting from 1e10 
    will extract numerical noise mismatch. We extract from the robust synchronized 
    mantissa layer (e.g. 1e3).
    """
    # Using 1e3 extracts the 1st to 3rd decimal places which are fully synchronized.
    # If error is ~1e-3, then the first two decimals are identical.
    # To be extremely safe, we use 1e2.
    keys = np.mod(np.abs(sync_states) * 1e2, 256).astype(np.uint8)
    return keys
