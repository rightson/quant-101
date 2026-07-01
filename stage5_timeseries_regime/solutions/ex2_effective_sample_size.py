#!/usr/bin/env python3
"""Stage 5 / 習題 2 參考解 — effective sample size:自相關如何壓低有效樣本.

執行:  python solutions/ex2_effective_sample_size.py
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from quant101 import data, timeseries as ts  # noqa: E402

data.build(prefer_real=False)
r = data.daily_returns(kind="simple")
rv = r.to_numpy()
n = len(rv)

# 1) 日報酬:幾乎不自相關 -> n_eff ≈ n
print(f"日報酬:        n={n}  n_eff={ts.effective_sample_size(rv):.0f}  (幾乎不自相關)")

# 2) overlapping H 日報酬:相鄰視窗共用 H-1 天 -> n_eff ≈ n/H
print("\noverlapping H 日報酬(文章式的『後續 N 日報酬』):")
for H in [5, 20, 60]:
    ov = pd.Series(rv).rolling(H).sum().dropna().to_numpy()
    ne = ts.effective_sample_size(ov)
    print(f"  H={H:2d}:  n={len(ov)}  n_eff={ne:.0f}  ->  n/n_eff={len(ov)/ne:.1f} (≈ H)")
print("=> 自相關把有效樣本壓成約 n/H。用 n 當自由度算的 SE/顯著性,嚴重灌水。")

# 3) 事件:9~10 個聚在循環高點的事件,有效樣本 < 事件數
# 用高波動 regime spell 數當『獨立事件叢集』的代理(完整版見 notebook)。
from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression  # noqa: E402
res = MarkovRegression(pd.Series(rv * 100), k_regimes=2, trend="c",
                       switching_variance=True).fit()
hi = int(np.argmax([res.params["sigma2[0]"], res.params["sigma2[1]"]]))
in_hi = (res.smoothed_marginal_probabilities[hi] > 0.5).to_numpy()

prices = data.load_prices()["close"].to_numpy()
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
drop_idx = np.clip(days + 4, 0, n - 1)
spells = ts.count_regime_spells(in_hi, drop_idx)
print(f"\n事件數 = {len(days)};  這些事件落在 {spells} 個不同的高波動 regime 叢集裡。")
print(f"=> 有效獨立事件數 ≈ {spells} < {len(days)}:同一波高波動裡的數個事件不是獨立抽樣。")
print("   對照文章:9~10 個事件多半擠在幾個循環高點/危機期,有效樣本遠 < 9。")
