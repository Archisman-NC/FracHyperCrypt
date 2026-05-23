import numpy as np
from scipy.special import gamma

class ABMSolver:
    """
    Fractional Adams-Bashforth-Moulton Predictor-Corrector Solver.
    Uses the Short Memory Principle (truncation) for O(N * L) scaling.
    """
    def __init__(self, q, dt, truncation_window=5000, dim=6):
        self.q = q
        self.h = dt
        self.L = truncation_window
        self.dim = dim
        
        # Precompute weights for the Predictor (b) and Corrector (a)
        self.b = np.zeros(self.L)
        self.a = np.zeros(self.L)
        
        coeff_p = (self.h ** self.q) / gamma(self.q + 1)
        coeff_c = (self.h ** self.q) / gamma(self.q + 2)
        
        # k goes from 1 to L
        for k in range(1, self.L + 1):
            # Predictor weight b_k
            self.b[k-1] = coeff_p * (k**self.q - (k-1)**self.q)
            
            # Corrector weight a_k (bulk formula)
            self.a[k-1] = coeff_c * ((k+1)**(self.q+1) - 2 * k**(self.q+1) + (k-1)**(self.q+1))
            
        self.a0 = coeff_c
        
        # Reverse weights so we can use np.dot directly with a chronologically ordered history buffer.
        # history = [x_{n+1-L}, ..., x_{n-1}, x_n]
        # memory_term = sum_{k=1}^L w_k x_{n+1-k}
        # which is exactly dot product of w[::-1] and history.
        self.b_rev = self.b[::-1].reshape(-1, 1)
        self.a_rev = self.a[::-1].reshape(-1, 1)

    def predict(self, x0, f_history):
        """
        Predicts the next state x_{n+1}^P.
        f_history should be a numpy array of shape (L_eff, dim), where L_eff <= L.
        """
        n = len(f_history)
        if n == 0:
            return np.copy(x0)
        
        # Select the appropriate number of reversed weights based on current history length
        b_eff = self.b_rev[-n:] 
        
        # np.sum(b_eff * f_history, axis=0) is equivalent to dot product over axis 0
        memory_p = np.sum(b_eff * f_history, axis=0)
        return x0 + memory_p

    def correct(self, x0, f_history, f_pred):
        """
        Corrects the state x_{n+1} using the predicted vector field f_pred.
        f_history should be a numpy array of shape (L_eff, dim).
        """
        n = len(f_history)
        if n == 0:
            return x0 + self.a0 * f_pred
        
        a_eff = self.a_rev[-n:]
        
        memory_c = np.sum(a_eff * f_history, axis=0)
        return x0 + memory_c + self.a0 * f_pred

