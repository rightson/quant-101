#!/usr/bin/env python3
"""Stage 1 / 習題 1 參考解 — Var(X̄)=σ²/n,數值驗證 + AR(1) 反例.

執行:  python solutions/ex1_se_derivation.py
"""
import numpy as np

rng = np.random.default_rng(1)

# --- 1-2) 手推見 lecture.md;這裡只做數值驗證 -------------------------------
mu, sigma = 0.05, 0.17
reps = 100_000

print("i.i.d. 母體  N(0.05, 0.17²):")
for n in (9, 100):
    means = rng.normal(mu, sigma, size=(reps, n)).mean(axis=1)
    emp_se = means.std()
    theo_se = sigma / np.sqrt(n)
    print(f"  n={n:4d}:  empirical SE={emp_se:.4f}   theory σ/√n={theo_se:.4f}")

# --- 4) AR(1) 反例:正自相關 ⟹ 真 SE > σ/√n ------------------------------
def ar1_paths(n, phi, reps, innov_sd):
    """生 reps 條長度 n 的 AR(1);邊際變異固定 = sigma² 以做公平比較."""
    x = np.zeros((reps, n))
    x[:, 0] = rng.normal(0, sigma, reps)         # 起點用穩態邊際分布
    for t in range(1, n):
        x[:, t] = phi * x[:, t - 1] + rng.normal(0, innov_sd, reps)
    return x

phi = 0.5
innov_sd = sigma * np.sqrt(1 - phi**2)           # 讓邊際 sd 仍 = sigma
n = 100
paths = ar1_paths(n, phi, reps, innov_sd)
emp_se_ar = paths.mean(axis=1).std()
naive_se = sigma / np.sqrt(n)
# 理論:Var(X̄) 對 AR(1) ≈ (σ²/n)·(1+φ)/(1-φ)
inflate = np.sqrt((1 + phi) / (1 - phi))
print(f"\nAR(1) φ={phi}, n={n} (邊際 sd 仍 = {sigma}):")
print(f"  naive σ/√n      = {naive_se:.4f}")
print(f"  empirical SE    = {emp_se_ar:.4f}")
print(f"  理論放大倍數 √((1+φ)/(1-φ)) = {inflate:.2f}  -> "
      f"naive×inflate = {naive_se*inflate:.4f}")
print("  => 有正自相關時,naive σ/√n 嚴重低估真實不確定性(Stage 5 主題).")
