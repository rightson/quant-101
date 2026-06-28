# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
# ---

# %% [markdown]
# # Stage 2 Notebook(完整樣板)— 重算文章三個數字的 CI 與 Power
#
# 這是 ★ 站的核心交付物。輸出全部對齊 gate 參考值:
# - Wilson CI(8/9) = **[0.565, 0.980]**;Wald 上界 > 1(壞掉)
# - power(d≈0.464, n=9) ≈ **0.233**;達 0.8 需 **n≈39**
# - effect-size × n → power 熱力圖,標出 n=9
#
# 跑法:`python notebook_stage2.py`(會把圖存到 figures/)。

# %%
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from quant101 import stats as q  # noqa: E402

# %% [markdown]
# ## 數字 1 —「88% = 8/9」的比例區間
#
# 對單一比例,小樣本 + p̂ 接近 1,Wald 會溢出 [0,1];正解是 Wilson。

# %%
k, n = 8, 9
print(f"p̂ = {k}/{n} = {k/n:.4f}")
for name, fn in [("Wald", q.wald_ci), ("Wilson", q.wilson_ci),
                 ("Agresti-Coull", q.agresti_coull_ci),
                 ("Clopper-Pearson", q.clopper_pearson_ci)]:
    lo, hi = fn(k, n)
    print(f"  {name:16s}: [{lo:.3f}, {hi:.3f}]" + ("   <-- 上界>1!" if hi > 1 else ""))
print("=> 88% 很猛,但 Wilson 區間從 56.5% 蓋到 98% —— 真實命中率可能只有五成多。")

# %% [markdown]
# ## 數字 2 —「平均 +4.7%」的信賴區間(小樣本 t)
#
# 用 9 筆示意年報酬代表事件後報酬,展示點估計背後的寬區間。

# %%
returns_9 = np.array([0.085, -0.12, 0.21, -0.05, 0.30, -0.017, 0.11, -0.23, 0.16])
lo, hi = q.t_ci_mean(returns_9)
print(f"x̄={returns_9.mean():+.2%}  SE={q.se_mean(returns_9):.2%}  95% t-CI=[{lo:+.2%}, {hi:+.2%}]")
print("=> 一個『平均約 +5%』其實寬到 −8%~+18%,跟 buy-and-hold +8.5% 分不開。")

# %% [markdown]
# ## 數字 3 —「1Y 中位 −1.7% vs buy-and-hold +8.5%」的 power
# %%
mean_diff = 0.085 - (-0.017)       # 10.2pp
sigma = 0.22
d = mean_diff / sigma
pw9 = q.power_one_sample_t(d, 9)
n80 = q.n_for_power_one_sample_t(d, 0.8)
print(f"Cohen's d = {d:.4f}")
print(f"power(n=9) = {pw9:.4f}  (< 0.3 ✓)")
print(f"n for power=0.8 = {n80}")
print("=> n=9 偵測這個效果的機率不到 1/4;『沒看到顯著』不是『沒效果』的證據。")

# %% [markdown]
# ## 熱力圖:effect size × n → power,標出 n=9
# %%
d_grid = np.linspace(0.1, 1.2, 45)
n_grid = np.arange(5, 81)
P = np.array([[q.power_one_sample_t(dd, nn) for nn in n_grid] for dd in d_grid])

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 5))
    im = ax.imshow(P, origin="lower", aspect="auto", cmap="viridis",
                   extent=[n_grid[0], n_grid[-1], d_grid[0], d_grid[-1]],
                   vmin=0, vmax=1)
    cs = ax.contour(n_grid, d_grid, P, levels=[0.8], colors="white", linewidths=2)
    ax.clabel(cs, fmt="power=0.8")
    ax.axvline(9, color="red", lw=2, ls="--", label="n=9 (article)")
    ax.plot(9, d, "r*", ms=16, label=f"article case (d={d:.2f}, power={pw9:.2f})")
    ax.set(xlabel="sample size n", ylabel="effect size (Cohen's d)",
           title="one-sample t-test power  (α=0.05, two-sided)")
    ax.legend(loc="upper right")
    fig.colorbar(im, ax=ax, label="power")
    out = Path(__file__).resolve().parents[1] / "figures"
    out.mkdir(exist_ok=True)
    fig.tight_layout()
    fig.savefig(out / "stage2_power_heatmap.png", dpi=120)
    print(f"saved -> {out/'stage2_power_heatmap.png'}")
except Exception as exc:
    print(f"(heatmap skipped: {exc})")

# n=9 那一整行的 power
col9 = P[:, list(n_grid).index(9)]
print(f"\nn=9 那一行 power 範圍:{col9.min():.2f} ~ {col9.max():.2f}"
      f"(只有 d>{d_grid[np.argmax(col9>=0.8)] if (col9>=0.8).any() else 1.2:.2f} 才到 0.8)")

# %% [markdown]
# ## 過 gate 的總結
# | 數字 | 結果 |
# |---|---|
# | Wilson CI(8/9) | **[0.565, 0.980]** |
# | Wald CI(8/9) | [0.684, 1.094] ← 上界>1,不可用 |
# | power(d≈0.464, n=9) | **≈ 0.233** |
# | n for power=0.8 | **≈ 39** |
#
# 結論:文章的「88%」「+4.7%」「−1.7% vs +8.5%」在 n=9 下都被雜訊吞沒——
# 寬到沒用的 CI 與低到沒用的 power,是同一件事的兩種講法。
