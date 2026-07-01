#!/usr/bin/env python3
"""Stage 4 / 習題 2 參考解 — permutation test:事件後報酬 vs 隨機同窗報酬.

執行:  python solutions/ex2_permutation_test.py
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from quant101 import data, resample as R  # noqa: E402

data.build(prefer_real=False)                       # 確保有資料
returns = data.daily_returns(kind="simple").to_numpy()
prices = data.load_prices()["close"].to_numpy()
n = len(returns)
horizon = 5                                         # 事件後看 5 日單日報酬(非重疊)

# 事件:創 252 日新高 -> 之後 4 日內出現「過去一年最慘 2%」急殺
def event_days(lookback=252, drop_days=4, worst_pct=0.02, cooldown=10):
    import pandas as pd
    roll_max = pd.Series(prices).rolling(lookback).max().to_numpy()
    thr = pd.Series(returns).rolling(lookback).quantile(worst_pct).to_numpy()
    days, last = [], -10**9
    for t in range(lookback, n - drop_days - horizon - 1):
        if t - last < cooldown:
            continue
        if prices[t] >= roll_max[t] and returns[t + 1:t + 1 + drop_days].min() <= thr[t]:
            days.append(t); last = t
    return np.array(days, dtype=int)


days = event_days()
event_out = returns[days + 4 + horizon]             # 事件(急殺窗口)後的單日報酬
# 對照:所有「非事件」日的同 offset 單日報酬
mask = np.ones(n, dtype=bool)
mask[np.clip(days + 4 + horizon, 0, n - 1)] = False
baseline = returns[4 + horizon:][mask[4 + horizon:]]

print(f"[data: {'synthetic' if data.is_synthetic() else 'real ^TWII'}]")
print(f"事件數 = {len(days)};  事件後報酬均值 = {event_out.mean():+.4%};  "
      f"對照均值 = {baseline.mean():+.4%}")

obs, p = R.permutation_test(event_out, baseline, n_perm=20000,
                            alternative="two-sided", seed=3)
print(f"\npermutation test(差異 = 事件均值 − 對照均值):")
print(f"  observed diff = {obs:+.4%}")
print(f"  empirical p   = {p:.3f}")
print(
    "\n判讀:permutation test 不假設常態、直接打亂標籤建立 null。"
    f"\n在(無動能的)合成資料上 p={p:.2f} ⇒ 事件後報酬與隨機同窗報酬分布無異——"
    "\n『急殺後會怎樣』看不出任何有別於隨機的結構。"
)
