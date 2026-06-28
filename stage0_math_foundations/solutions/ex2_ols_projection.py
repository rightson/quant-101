#!/usr/bin/env python3
"""Stage 0 / 習題 2 參考解 — OLS = 把 Y 投影到 col(X).

驗證三種算法給出同一個 Ŷ,且殘差與 col(X) 正交.
執行:  python solutions/ex2_ols_projection.py
"""
import numpy as np

rng = np.random.default_rng(0)
n = 200
# design matrix: intercept + 2 regressors (e.g. market return, momentum)
X = np.column_stack([np.ones(n), rng.normal(size=n), rng.normal(size=n)])
beta_true = np.array([0.001, 0.8, 0.3])
Y = X @ beta_true + rng.normal(scale=0.5, size=n)

# (a) closed form: β̂ = (XᵀX)⁻¹ XᵀY
beta_cf = np.linalg.inv(X.T @ X) @ X.T @ Y
Yhat_cf = X @ beta_cf

# (b) lstsq
beta_ls, *_ = np.linalg.lstsq(X, Y, rcond=None)
Yhat_ls = X @ beta_ls

# (c) explicit projection via hat matrix H = X(XᵀX)⁻¹Xᵀ
H = X @ np.linalg.inv(X.T @ X) @ X.T
Yhat_H = H @ Y

print("β̂ (closed form) =", np.round(beta_cf, 4))
print("β̂ (lstsq)       =", np.round(beta_ls, 4))
print("max |Ŷ_cf - Ŷ_ls| =", np.max(np.abs(Yhat_cf - Yhat_ls)))
print("max |Ŷ_cf - Ŷ_H | =", np.max(np.abs(Yhat_cf - Yhat_H)))

# H is idempotent & symmetric (a projection)
print("‖H² - H‖ =", np.linalg.norm(H @ H - H))
print("‖Hᵀ - H‖ =", np.linalg.norm(H.T - H))

# residual orthogonal to col(X): Xᵀe ≈ 0
e = Y - Yhat_cf
print("‖Xᵀe‖ =", np.linalg.norm(X.T @ e), "(≈0 ⟹ 殘差 ⟂ col(X))")

assert np.allclose(Yhat_cf, Yhat_ls)
assert np.allclose(Yhat_cf, Yhat_H)
assert np.allclose(X.T @ e, 0, atol=1e-8)
print("\nOK — OLS 就是把 Y 正交投影到 X 張成的子空間;殘差是投影掉的部分。")
