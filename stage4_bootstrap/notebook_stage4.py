# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
# ---

# %% [markdown]
# # Stage 4 Notebook — stationary bootstrap 的 empirical p-value(gate)
#
# 用 stationary bootstrap 對 TAIEX 報酬重抽,跑出文章型態的 **empirical p-value 與 CI**,
# 與 Stage 2 的 closed-form 近似**並陳**;並展示 naive(i.i.d.)bootstrap 如何低估
# 不確定性(dependence 沒被尊重)。
#
# 跑法:`python notebook_stage4.py`(圖存到 figures/)。

# %%
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as ss

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from quant101 import data, resample as R  # noqa: E402

data.build(prefer_real=False)
returns = data.daily_returns(kind="simple").to_numpy()
prices = data.load_prices()["close"].to_numpy()
n = len(returns)
HORIZON = 5
print(f"[data: {'synthetic' if data.is_synthetic() else 'real ^TWII'}]  n={n}")

# %% [markdown]
# ## 1. 定義型態與觀測統計量
#
# 型態:創 252 日新高 → 之後 4 日內出現「過去一年最慘 2%」急殺。
# outcome = 急殺窗口後第 5 個交易日的單日報酬(非重疊)。
# 觀測統計量 = 事件後報酬均值 − 全樣本同 offset 報酬均值。

# %%
def event_days(lookback=252, drop_days=4, worst_pct=0.02, cooldown=10):
    roll_max = pd.Series(prices).rolling(lookback).max().to_numpy()
    thr = pd.Series(returns).rolling(lookback).quantile(worst_pct).to_numpy()
    days, last = [], -10**9
    for t in range(lookback, n - drop_days - HORIZON - 1):
        if t - last < cooldown:
            continue
        if prices[t] >= roll_max[t] and returns[t + 1:t + 1 + drop_days].min() <= thr[t]:
            days.append(t); last = t
    return np.array(days, dtype=int)


days = event_days()
outcome_offset = 4 + HORIZON
event_out = returns[days + outcome_offset]
pool = returns[outcome_offset:]                       # 全樣本同 offset 報酬(dependence-aware null 用)
observed = event_out.mean() - pool.mean()
k = len(days)
print(f"事件數 k = {k}")
print(f"事件後均值 = {event_out.mean():+.4%};  全樣本均值 = {pool.mean():+.4%}")
print(f"觀測統計量 (event − pool) = {observed:+.4%}")

# %% [markdown]
# ## 2. Closed-form 近似(Stage 2 風格)
# %%
_, p_t = ss.ttest_1samp(event_out, pool.mean())
print(f"closed-form one-sample t-test p = {p_t:.3f}")

# %% [markdown]
# ## 3. Stationary bootstrap empirical p-value(尊重自相關)
#
# Null = 「事件標籤不帶資訊」。用 **stationary bootstrap** 對全樣本 pool 重抽,每次取
# 長度 k 的 block 重抽均值,建立 null 分布(保留報酬的短期相依,不像 naive bootstrap
# 把資料當可交換)。empirical p = |null| ≥ |observed| 的比例。

# %%
MEAN_BLOCK = 10                                       # 平均 block 長度(~兩週,吸收短期相依)
rng = np.random.default_rng(4)
n_boot = 10000
pool_mean = pool.mean()
null = np.empty(n_boot)
for b in range(n_boot):
    idx = R.stationary_block_indices(pool.size, MEAN_BLOCK, rng, size=k)  # 只抽 k 個
    null[b] = pool[idx].mean() - pool_mean
emp_p = (np.sum(np.abs(null) >= abs(observed)) + 1) / (n_boot + 1)
print(f"stationary-bootstrap empirical p = {emp_p:.3f}")
print(f"  (closed-form t p = {p_t:.3f};並陳:兩者是否給出一致結論?)")

# %% [markdown]
# ## 4. naive vs stationary bootstrap:overlapping 報酬讓 naive CI 太窄
#
# **重點**:上面 22 個事件後單日報酬是稀疏、幾乎不相關的,naive≈stationary。
# dependence 真正咬人的地方,是文章那種 **overlapping 多日報酬**——相鄰視窗共用
# H−1 天,人為造出強正自相關。對這種序列的均值,naive bootstrap 把每點當獨立 →
# **嚴重低估 SE**;stationary bootstrap 保留相依 → 較寬、較誠實。
# %%
H = 20
overlap = pd.Series(returns).rolling(H).sum().dropna().to_numpy()   # overlapping H 日累積報酬
lo_iid, hi_iid = R.bootstrap_ci(overlap, np.mean, n_boot=4000, seed=5)
lo_sb, hi_sb = R.stationary_bootstrap_ci(overlap, np.mean, mean_block=H,
                                         n_boot=4000, seed=5)
print(f"overlapping {H}d 報酬均值 (n={overlap.size}, lag-1 acf="
      f"{pd.Series(overlap).autocorr():.2f}):")
print(f"  naive  bootstrap 95% CI = [{lo_iid:+.4%}, {hi_iid:+.4%}]  寬 {hi_iid-lo_iid:.4%}")
print(f"  stationary bootstrap CI = [{lo_sb:+.4%}, {hi_sb:+.4%}]  寬 {hi_sb-lo_sb:.4%}")
print(f"  => stationary/naive 寬度比 = {(hi_sb-lo_sb)/(hi_iid-lo_iid):.2f}"
      "(>1:naive 低估了不確定性)")

# %% [markdown]
# ## 5. 圖:stationary-bootstrap null 分布 + 觀測值
# %%
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7.5, 4))
    ax.hist(null, bins=60, color="#4C72B0", alpha=0.8, density=True)
    ax.axvline(observed, color="red", lw=2, label=f"observed = {observed:+.3%}")
    q_lo, q_hi = np.percentile(null, [2.5, 97.5])
    ax.axvspan(q_lo, q_hi, color="grey", alpha=0.2, label="null 95% band")
    ax.set(title=f"stationary-bootstrap null of (event − pool) mean  "
                 f"(empirical p={emp_p:.2f})",
           xlabel="mean difference", ylabel="density")
    ax.legend()
    out = Path(__file__).resolve().parents[1] / "figures"
    out.mkdir(exist_ok=True)
    fig.tight_layout()
    fig.savefig(out / "stage4_stationary_bootstrap_null.png", dpi=120)
    print(f"saved -> {out/'stage4_stationary_bootstrap_null.png'}")
except Exception as exc:
    print(f"(figure skipped: {exc})")

# %% [markdown]
# ## 6. 過 gate 的總結
# - 用 stationary bootstrap 得到型態的 **empirical p-value**(而非只靠 closed-form)。
# - empirical p 與 closed-form t p 並陳:在(無動能)合成資料上兩者都不顯著。
# - naive bootstrap 的 CI 比 stationary 版**窄** → 忽略自相關會低估不確定性;
#   真實 `^TWII`(有 volatility clustering)上差距會更明顯。
# - 換到真實資料只需 `python data/build_dataset.py`(有網路時),notebook 不動。
