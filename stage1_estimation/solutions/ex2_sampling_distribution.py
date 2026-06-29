#!/usr/bin/env python3
"""Stage 1 / 習題 2 參考解 — n=9 vs n=100 sampling distribution.

執行:  python solutions/ex2_sampling_distribution.py
(會嘗試存一張圖到 figures/;沒有顯示環境也能跑.)
"""
from pathlib import Path

import numpy as np

rng = np.random.default_rng(2)

mu, sigma = 0.05, 0.17
reps = 10_000

means9 = rng.normal(mu, sigma, size=(reps, 9)).mean(axis=1)
means100 = rng.normal(mu, sigma, size=(reps, 100)).mean(axis=1)

se9, se100 = means9.std(), means100.std()
print(f"SE(n=9)   = {se9:.4f}   (theory {sigma/3:.4f})")
print(f"SE(n=100) = {se100:.4f}   (theory {sigma/10:.4f})")
print(f"ratio SE(100)/SE(9) = {se100/se9:.3f}   "
      f"(theory √(9/100)=0.300)")
print("=> n=100 的 sampling distribution 寬度約是 n=9 的 1/3.33 ≈ 0.3,"
      "亦即區間縮成約 1/3。")

# optional figure
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7, 4))
    bins = np.linspace(mu - 0.6, mu + 0.6, 80)
    ax.hist(means9, bins=bins, alpha=0.5, density=True, label="n=9")
    ax.hist(means100, bins=bins, alpha=0.6, density=True, label="n=100")
    ax.axvline(mu, color="k", lw=1, ls="--", label="true μ")
    ax.set(title="Sampling distribution of X̄  (σ=0.17)",
           xlabel="sample mean", ylabel="density")
    ax.legend()
    out = Path(__file__).resolve().parents[2] / "figures"
    out.mkdir(exist_ok=True)
    fig.tight_layout()
    fig.savefig(out / "stage1_sampling_distribution.png", dpi=110)
    print(f"saved figure -> {out/'stage1_sampling_distribution.png'}")
except Exception as exc:
    print(f"(figure skipped: {exc})")
