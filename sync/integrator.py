import numpy as np
from scipy.special import gamma

class FractionalIntegrator:
    """
    Computes numerical fractional integration I^q using finite history buffering.
    We use the same Adams-Bashforth weights (b_k) to integrate.
    Since D^{-q} x(t) = I^q x(t), we apply weights corresponding to order -q.
    Wait, actually the fractional integral I^q is computed exactly as the predictor 
    step of ABM solver but with q instead of -q, because the ABM solver computes I^q(f).
    Therefore, I^q(e) = (h^q / Gamma(q+1)) sum b_k * e_{n-k}
    where b_k = k^q - (k-1)^q.
    """
    def __init__(self, q, dt, truncation_window=5000, dim=6):
        self.q = q
        self.h = dt
        self.L = truncation_window
        self.dim = dim
        
        self.b = np.zeros(self.L)
        coeff_p = (self.h ** self.q) / gamma(self.q + 1)
        
        for k in range(1, self.L + 1):
            self.b[k-1] = coeff_p * (k**self.q - (k-1)**self.q)
            
        self.b_rev = self.b[::-1].reshape(-1, 1)

    def integrate(self, history):
        """
        history: (L_eff, dim) chronologically ordered buffer
        """
        n = len(history)
        if n == 0:
            return np.zeros(self.dim)
        
        b_eff = self.b_rev[-n:]
        return np.sum(b_eff * history, axis=0)

