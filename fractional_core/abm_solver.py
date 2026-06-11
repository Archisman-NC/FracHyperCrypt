import numpy as np
from scipy.special import gamma

class ABMSolver:
    """
    Fractional Adams-Bashforth-Moulton Predictor-Corrector Solver.
    Uses the Short Memory Principle (truncation) for O(N * L) scaling.
    Mathematically corrected to align strictly with Diethelm's formulation,
    specifically fixing the Newton-Cotes weight for the t_0 boundary node.
    """
    def __init__(self, q, dt, truncation_window=5000, dim=6):
        self.q = q
        self.h = dt
        self.L = truncation_window
        self.dim = dim
        self.internal_step = 0  # Tracks absolute steps to handle startup boundary conditions
        
        # Precompute weights for the Predictor (b) and Corrector (a)
        self.b = np.zeros(self.L, dtype=np.float64)
        self.a = np.zeros(self.L, dtype=np.float64)
        
        self.coeff_p = (self.h ** self.q) / gamma(self.q + 1)
        self.coeff_c = (self.h ** self.q) / gamma(self.q + 2)
        
        # k goes from 1 to L
        for k in range(1, self.L + 1):
            # Predictor weight b_{j, n+1} where k = n + 1 - j
            self.b[k-1] = self.coeff_p * (k**self.q - (k-1)**self.q)
            
            # Corrector bulk weight a_{j, n+1} where k = n + 1 - j
            self.a[k-1] = self.coeff_c * ((k+1)**(self.q+1) - 2 * k**(self.q+1) + (k-1)**(self.q+1))
            
        self.a0 = self.coeff_c
        
        # Reverse weights so we can use np.dot directly with a chronologically ordered history buffer.
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
        
        # Predictor sum
        memory_p = np.sum(b_eff * f_history, axis=0)
        return x0 + memory_p

    def correct(self, x0, f_history, f_pred):
        """
        Corrects the state x_{n+1} using the predicted vector field f_pred.
        f_history should be a numpy array of shape (L_eff, dim).
        """
        n = len(f_history)
        if n == 0:
            self.internal_step += 1
            return x0 + self.a0 * f_pred
        
        absolute_n = self.internal_step + 1
        
        a_eff = np.copy(self.a_rev[-n:])
        
        # MATHEMATICAL CORRECTION:
        # In Diethelm's formulation, the Newton-Cotes weight for the boundary node j=0 (at t_0) 
        # is fundamentally different from the bulk interpolant nodes. 
        # If absolute_n <= self.L, then f_history[0] still represents the true initial condition f(t_0).
        if absolute_n <= self.L:
            # For the step computing x_{m+1}, the history buffer has m elements, so m = absolute_n - 1.
            m = absolute_n - 1
            a_0_m_plus_1 = self.coeff_c * (m**(self.q + 1) - (m - self.q) * (m + 1)**self.q)
            # The weight for f_history[0] is at index 0 of a_eff
            a_eff[0, 0] = a_0_m_plus_1
            
        memory_c = np.sum(a_eff * f_history, axis=0)
        
        self.internal_step += 1
        return x0 + memory_c + self.a0 * f_pred


