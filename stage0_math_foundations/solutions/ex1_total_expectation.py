#!/usr/bin/env python3
"""Stage 0 / 習題 1 參考解 — joint -> marginal / conditional / 全期望.

手算與程式對照。執行:  python solutions/ex1_total_expectation.py
"""
import numpy as np

# joint P(X, Y).  rows = X in {0,1}; cols = Y in {-10%, 0%, +10%}
y_vals = np.array([-0.10, 0.00, 0.10])
joint = np.array([
    [0.20, 0.30, 0.10],   # X = 0  (no new high)
    [0.05, 0.15, 0.20],   # X = 1  (new high)
])
assert np.isclose(joint.sum(), 1.0)

# 1) marginals
p_X = joint.sum(axis=1)            # P(X=0), P(X=1)
p_Y = joint.sum(axis=0)            # P(Y=-10), P(Y=0), P(Y=+10)
print("P(X)  =", p_X, "  -> P(X=1 創新高) =", p_X[1])
print("P(Y)  =", p_Y)

# 2) conditionals: P(Y|X=x) = joint row / marginal of X   (conditional = joint ÷ marginal)
p_Y_given_X1 = joint[1] / p_X[1]
p_Y_given_X0 = joint[0] / p_X[0]
print("P(Y|X=1) =", p_Y_given_X1)
print("P(Y|X=0) =", p_Y_given_X0)

# 3) conditional & unconditional expectations
E_Y_given_X1 = (y_vals * p_Y_given_X1).sum()
E_Y_given_X0 = (y_vals * p_Y_given_X0).sum()
E_Y = (y_vals * p_Y).sum()
print(f"E[Y|X=1] = {E_Y_given_X1:+.4f}")
print(f"E[Y|X=0] = {E_Y_given_X0:+.4f}")
print(f"E[Y]     = {E_Y:+.4f}")

# 4) law of total expectation
E_Y_via_lote = E_Y_given_X1 * p_X[1] + E_Y_given_X0 * p_X[0]
print(f"E[Y] via LOTE = {E_Y_via_lote:+.4f}  (should equal E[Y])")
assert np.isclose(E_Y, E_Y_via_lote)

# 5) the point
gap = E_Y_given_X1 - E_Y
print(f"\nE[Y|創新高] - E[Y] = {gap:+.4f}")
print(
    "為什麼是正的:創新高那一列把質量往 Y=+10% 推(0.20/0.40=50%),"
    "純粹是 conditioning 挑了動能為正的子母體。不需要『主力』。"
)
