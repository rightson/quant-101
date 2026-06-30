# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
# ---

# %% [markdown]
# # Stage 3 Notebook — 事件定義 grid search 與 multiple-testing 校正
#
# 把文章的事件定義參數化,對(合成、無內建訊號的)TAIEX 跑整個 grid,展示:
# 1. 「顯著」cell 隨參數**漂移**——同一份資料,換個定義就翻盤;
# 2. raw 顯著比例 ≈ α(因為合成資料沒有真訊號,單一檢定已校準);
# 3. Bonferroni / Holm / BH 校正後幾乎**全滅**。
#
# 跑法:`python notebook_stage3.py`(會把 p 值熱力圖存到 figures/)。

# %%
import sys
from pathlib import Path

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from quant101 import data, stats as q  # noqa: E402

# %% [markdown]
# ## 1. 資料與單一變體的檢定
#
# outcome 取「急殺窗口『之後』的單日報酬」(非重疊)+ cooldown,確保**單一**檢定校準到 ~α;
# 如此唯一灌大假陽性的就是 grid 的格數(multiplicity)。
# (文章實際用的是 overlapping 多日 horizon —— 那會*額外*灌水,是 Stage 5/7 的另一個錯。)

# %%
import pandas as pd  # noqa: E402

src = "synthetic" if data.is_synthetic() else "real ^TWII"
print(f"[data source: {src}]")
ret_s = data.daily_returns(kind="simple")
returns = ret_s.to_numpy()
prices = data.load_prices()["close"].to_numpy()
n = len(returns)


def event_days(lookback, drop_days, worst_pct, cooldown=10):
    """回傳符合『創 lookback 新高 -> drop_days 內急殺到 worst_pct 門檻』的事件日 index."""
    roll_max = pd.Series(prices).rolling(lookback).max().to_numpy()
    thr = ret_s.rolling(lookback).quantile(worst_pct).to_numpy()
    days, last = [], -10**9
    for t in range(lookback, n - drop_days - 22):
        if t - last < cooldown:
            continue
        if prices[t] >= roll_max[t] and returns[t + 1:t + 1 + drop_days].min() <= thr[t]:
            days.append(t)
            last = t
    return np.array(days, dtype=int)


def test_offset(days, drop_days, offset):
    """outcome = 急殺窗口後第 offset 個交易日的單日報酬(非重疊 -> 校準到 α)."""
    idx = days + drop_days + offset
    idx = idx[idx < n]
    out = returns[idx]
    if out.size < 5:
        return np.nan, out.size
    _, p = stats.ttest_1samp(out, 0.0)
    return p, out.size


# %% [markdown]
# ## 2. Grid search 全部組合
#
# 5 個 researcher DoF 中掃 4 個:lookback × drop_days × worst_pct × 評估日 offset。
# (offset = 看「事件後第幾天」的報酬,本身就是一個沒被講出來的選擇。)
# %%
lookbacks = [126, 189, 252, 378]
drop_days_grid = [2, 3, 4, 5]
worst_pcts = [0.01, 0.02, 0.05, 0.10]
offsets = [1, 2, 3, 5, 10, 21]

rows = []
for lb in lookbacks:
    for dd in drop_days_grid:
        for wp in worst_pcts:
            days = event_days(lb, dd, wp)
            for off in offsets:
                p, k = test_offset(days, dd, off)
                rows.append((lb, dd, wp, off, p, k))

pvals = np.array([r[4] for r in rows])
valid = np.isfinite(pvals)
pv = pvals[valid]
print(f"grid 大小 = {len(rows)} 組;有效檢定 = {valid.sum()}")
print(f"raw 顯著 (p<.05) = {(pv<0.05).sum()}   (理論期望 ≈ {pv.size*0.05:.1f})")

# 最「漂亮」的一組
best_i = int(np.nanargmin(pvals))
blb, bdd, bwp, boff, bp, bk = rows[best_i]
print(f"最顯著組: lookback={blb}, drop_days={bdd}, worst_pct={bwp}, offset={boff} "
      f"-> p={bp:.4f}, n_events={bk}  <-- 報告時只講這一組就很唬人")

# %% [markdown]
# ## 3. 校正:把它放回它所屬的比較家族
# %%
for name, fn in [("Bonferroni", q.bonferroni), ("Holm", q.holm),
                 ("BH (FDR)", q.benjamini_hochberg)]:
    rej, padj = fn(pv, 0.05)
    print(f"  {name:12s}: 存活 {int(rej.sum())} 組;最顯著組 p_adj = {padj[np.argmin(pv)]:.3f}")
print("=> 校正後幾乎全滅;那個『最顯著』組的 adjusted p 一點都不顯著了。")

# %% [markdown]
# ## 4. 顯著性隨參數漂移:p 值熱力圖
#
# 每個 subplot 固定一個評估日 offset,畫 (worst_pct × lookback) 的 p 值(drop_days 取最顯著值)。
# 看「顯著」的星號怎麼隨著參數跳來跳去——同一份無訊號資料,換個定義就翻盤。
# %%
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    show_offsets = [1, 3, 5, 21]
    fig, axes = plt.subplots(1, len(show_offsets), figsize=(4 * len(show_offsets), 3.4),
                             sharey=True)
    for ax, off in zip(axes, show_offsets):
        grid = np.full((len(worst_pcts), len(lookbacks)), np.nan)
        for (lb, d, wp, o, p, k) in rows:
            if o != off:
                continue
            i, j = worst_pcts.index(wp), lookbacks.index(lb)
            # 取該 (wp, lb) 在各 drop_days 中最小的 p(模擬「挑最漂亮的講」)
            if np.isnan(grid[i, j]) or (np.isfinite(p) and p < grid[i, j]):
                grid[i, j] = p
        im = ax.imshow(grid, vmin=0, vmax=1, cmap="RdYlGn_r", aspect="auto", origin="lower")
        for i in range(len(worst_pcts)):
            for j in range(len(lookbacks)):
                if np.isfinite(grid[i, j]) and grid[i, j] < 0.05:
                    ax.text(j, i, "*", ha="center", va="center", color="white", fontsize=16)
        ax.set(title=f"offset={off}d", xlabel="lookback")
        ax.set_xticks(range(len(lookbacks)), lookbacks)
        ax.set_yticks(range(len(worst_pcts)), worst_pcts)
    axes[0].set_ylabel("worst_pct")
    fig.suptitle("raw p-value across event definitions  (* = p<0.05, no real signal in synthetic data)")
    fig.colorbar(im, ax=axes, label="raw p-value", fraction=0.02)
    out = Path(__file__).resolve().parents[1] / "figures"
    out.mkdir(exist_ok=True)
    fig.savefig(out / "stage3_pvalue_grid.png", dpi=120, bbox_inches="tight")
    print(f"saved -> {out/'stage3_pvalue_grid.png'}")
except Exception as exc:
    print(f"(heatmap skipped: {exc})")

# %% [markdown]
# ## 5. 過 gate 的總結
# - 文章定義含 5 個 researcher DoF(此 notebook 掃了其中 3 個 × horizon 隱含更多)。
# - 全部都是噪音時,`P(≥1 raw 顯著) ≈ 1`;raw 顯著比例 ≈ α。
# - 「最顯著」那組數字漂亮,但放回比較家族、做 Bonferroni/Holm/BH 校正後失去顯著。
# - **任何「我試了很多參數後發現…」都要先問:試了幾組?校正了嗎?out-of-sample 還在嗎?**
