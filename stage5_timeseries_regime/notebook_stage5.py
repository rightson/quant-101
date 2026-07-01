# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
# ---

# %% [markdown]
# # Stage 5 Notebook — Markov-switching regime 與「訊號是不是 regime proxy」(gate)
#
# 用 2-regime Markov-switching model 把 1999–2026 切成高/低波動 regime,檢定文章型態的
# 事件是否 **cluster 在特定 regime**。若是,則這個「訊號」多半只是「處於某個 regime」的
# proxy,而不是獨立的 edge。
#
# 跑法:`python notebook_stage5.py`(圖存到 figures/;需要 statsmodels)。

# %%
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from quant101 import data, timeseries as ts  # noqa: E402
from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression  # noqa: E402

data.build(prefer_real=False)
r = data.daily_returns(kind="simple")
rv = r.to_numpy()
prices = data.load_prices()["close"].to_numpy()
dates = data.load_prices().index[1:]
n = len(rv)
print(f"[data: {'synthetic' if data.is_synthetic() else 'real ^TWII'}]  n={n}")

# %% [markdown]
# ## 1. 配 2-regime Markov-switching(switching variance)
#
# 讓每個 regime 有自己的變異數;模型自己找出高波動/低波動兩個狀態與其轉移機率。

# %%
res = MarkovRegression(pd.Series(rv * 100), k_regimes=2, trend="c",
                       switching_variance=True).fit()
sig2 = [res.params["sigma2[0]"], res.params["sigma2[1]"]]
hi = int(np.argmax(sig2))
in_hi = (res.smoothed_marginal_probabilities[hi] > 0.5).to_numpy()
P = res.regime_transition[:, :, 0]
print(f"regime 變異數(日%²): 低={min(sig2):.2f}  高={max(sig2):.2f}  "
      f"(高波動 σ 約為低波動的 {np.sqrt(max(sig2)/min(sig2)):.1f} 倍)")
print(f"轉移持續性: P[留在低]={P[0,0]:.3f}  P[留在高]={P[1,1]:.3f}  "
      "(接近 1 ⇒ 是真的 regime,不是隨機跳動)")
print(f"高波動 regime 佔全期 {in_hi.mean():.1%} 的日子")

# %% [markdown]
# ## 2. 定義型態事件
#
# 創 252 日新高 → 之後 4 日內出現「過去一年最慘 2%」急殺(同前站)。

# %%
def event_days(lookback=252, drop_days=4, worst_pct=0.02, cooldown=10):
    rm = pd.Series(prices).rolling(lookback).max().to_numpy()
    thr = pd.Series(rv).rolling(lookback).quantile(worst_pct).to_numpy()
    days, last = [], -10**9
    for t in range(lookback, n - drop_days - 6):
        if t - last < cooldown:
            continue
        if prices[t] >= rm[t] and rv[t + 1:t + 1 + drop_days].min() <= thr[t]:
            days.append(t); last = t
    return np.array(days)

days = event_days()
drop_idx = np.clip(days + 4, 0, n - 1)      # regime 取急殺當天
print(f"事件數 k = {len(days)}")

# %% [markdown]
# ## 3. 檢定:事件是否 cluster 在高波動 regime?
#
# 比較「事件落在高波動 regime 的比例」與「高波動 regime 的全期基準率」,做 binomial test。

# %%
out = ts.regime_cluster_test(in_hi, drop_idx, alternative="greater")
print(f"高波動 regime 基準率      = {out['base_rate']:.1%}")
print(f"事件落在高波動 regime 比例 = {out['event_rate']:.1%}  ({out['k_in']}/{out['k']})")
print(f"binomial test p           = {out['p_value']:.3g}")
verdict = "是" if out["p_value"] < 0.05 else "否"
print(f"\n=> 事件顯著群聚於高波動 regime:{verdict}。"
      f"\n   訊號有多少是『身處高波動 regime』的 proxy,而非獨立 edge:{out['event_rate']-out['base_rate']:+.0%} 的超額集中。")

# %% [markdown]
# ## 4. 有效樣本:同一波高波動裡的事件不是獨立的
# %%
spells = ts.count_regime_spells(in_hi, drop_idx)
print(f"{len(days)} 個事件其實只落在 {spells} 個不同的高波動叢集 -> 有效獨立事件 ≈ {spells}")
print("對照文章:9~10 個事件多半擠在幾個循環頂/危機期,有效樣本遠 < 9(Stage 2 的 power 更糟)。")

# %% [markdown]
# ## 5. 圖:價格 + 高波動 regime 陰影 + 事件
# %%
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    px = prices[1:]                                   # align to returns/dates (len n)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(dates, px, lw=0.8, color="black", label="TAIEX (synthetic)")
    ax.fill_between(dates, px.min(), px.max(), where=in_hi,
                    color="#C44E52", alpha=0.15, label="high-vol regime")
    ax.scatter(dates[drop_idx], px[drop_idx], s=28, color="blue",
               zorder=5, label="pattern events")
    ax.set(title=f"events cluster in the high-vol regime "
                 f"({out['event_rate']:.0%} vs base {out['base_rate']:.0%}, p={out['p_value']:.1e})",
           xlabel="date", ylabel="index level")
    ax.legend(loc="upper left", fontsize=8)
    o = Path(__file__).resolve().parents[1] / "figures"; o.mkdir(exist_ok=True)
    fig.tight_layout(); fig.savefig(o / "stage5_regime_events.png", dpi=120)
    print(f"saved -> {o/'stage5_regime_events.png'}")
except Exception as exc:
    print(f"(figure skipped: {exc})")

# %% [markdown]
# ## 6. 過 gate 的判斷
# - 用 Markov-switching 把序列切成高/低波動 regime(轉移持續 ⇒ 真 regime)。
# - 事件**顯著群聚**於高波動 regime(合成資料上 p≈1e-7)⇒ **此訊號大半是 regime proxy**:
#   「創新高後急殺」幾乎就是「市場正處於高波動狀態」的另一種說法,不是獨立的 edge。
# - 且事件在時間上叢集 ⇒ 有效獨立樣本 < 事件數,Stage 2 的 power 分析還要再打折。
# - **注意**:合成資料只有 GARCH 造成的『波動 regime』,沒有牛熊循環;真實 `^TWII`
#   還會疊加『接近循環頂』的 regime,proxy 效果更強。換真實資料:`python data/build_dataset.py`。
