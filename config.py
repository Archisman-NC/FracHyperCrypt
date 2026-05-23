import numpy as np

# Fractional Dynamics Parameters
A = 0.5
B = 0.2
Q = 0.8

# Numerical Solver Parameters
DT = 0.005
L = 2000
STEPS = 15000

# Controller Parameters
ALPHA = 10.0
BETA = 5.0
THETA = 20.0
DELTA = 20.0
NU = 0.5
MU = 0.5
EPSILON = 1e-8
CLIP_LIMIT = 500.0

# Synchronization & Crypto Parameters
SYNC_THRESHOLD = 5e-2
DISCARD_STEPS = 5000
GAMMA = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0])
