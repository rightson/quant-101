# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
# ---

# %% [markdown]
# # Stage 1 Notebook — 「一個平均」其實有多抖
#
# 用純模擬(非 bootstrap)看「同母體抽 9 個」的 sample mean 散成什麼樣;
# 再把文章那 9 筆事件年報酬當「一次抽樣」,算它的 SE。
#
# 跑法:`python notebook_sampling.py`。

# %%
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from quant101 import stats as qstats  # noqa: E402

rng = np.random.default_rng(11)

# %% [markdown]
# ## 1. 純模擬:固定母體,抽 9 個,看 X̄ 跳多遠
#
# 母體 = 年報酬 `N(μ=5%, σ=17%)`(σ 取 TAIEX 量級)。我們抽 20 組各 9 個,
# 把每組的平均印出來——它們應該散得驚人。

# %%
mu, sigma = 0.05, 0.17
for i in range(20):
    sample = rng.normal(mu, sigma, size=9)
    print(f"  第{i+1:2d}組 9 筆的平均 = {sample.mean():+.2%}")
print(f"\n母體真值 μ = {mu:+.2%};理論 SE = σ/√9 = {sigma/3:.2%}")

# %% [markdown]
# ↑ 真值固定在 +5%,但「抽 9 個算平均」可以給你從負十幾趴到正十幾趴的數字。
# 一個 +4.7% 的單點,完全可能只是這種抖動的一次實現。

# %% [markdown]
# ## 2. sampling distribution:抽很多次,看整條分布
# %%
reps = 50_000
means9 = rng.normal(mu, sigma, size=(reps, 9)).mean(axis=1)
means100 = rng.normal(mu, sigma, size=(reps, 100)).mean(axis=1)
print(f"n=9   : 中心 {means9.mean():+.2%}  SE {means9.std():.2%}")
print(f"n=100 : 中心 {means100.mean():+.2%}  SE {means100.std():.2%}")
print(f"SE 比值 = {means100.std()/means9.std():.3f}  (理論 √(9/100)=0.300)")

# %% [markdown]
# ## 3. 把文章的 9 筆年報酬當「一次抽樣」
#
# 這 9 筆是「事件後一年報酬」的示意值(真實重算見 Stage 7 event study)。
# 重點是流程:給你 9 個數,你要會配 error bar。

# %%
returns_9 = np.array([0.085, -0.12, 0.21, -0.05, 0.30, -0.017, 0.11, -0.23, 0.16])
xbar = returns_9.mean()
s = returns_9.std(ddof=1)
se = qstats.se_mean(returns_9)
lo, hi = qstats.t_ci_mean(returns_9)
print(f"x̄  = {xbar:+.3%}")
print(f"s   = {s:.3%}")
print(f"SE  = s/√9 = {se:.3%}")
print(f"95% t-CI = [{lo:+.2%}, {hi:+.2%}]")
print("\n判讀:一個『平均 {:.1%}』其實是 [{:+.1%}, {:+.1%}],".format(xbar, lo, hi))
print("      它跟 buy-and-hold +8.5% 完全分不開。n=9 的 SE 把訊號吞了。")

# %% [markdown]
# ## 4. 過 gate 的三句話
# 1. SE = s/√n ≈ 5.8%(上面算出)。
# 2. sampling distribution:中心在 μ,散度 σ/√n,n 夠大時近似常態。
# 3. n 從 9→100,SE 縮 √(100/9)=10/3≈3.33 倍,故區間縮成約 1/3。
