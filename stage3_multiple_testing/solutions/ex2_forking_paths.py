#!/usr/bin/env python3
"""Stage 3 / 習題 2 參考解 — garden of forking paths 的實證.

對純噪音序列跑 m 個型態變體,展示「總會撈到幾個顯著」,且校正後歸零.
執行:  python solutions/ex2_forking_paths.py

設計重點:這一站要隔離的是「多重比較」效應,所以每個*單一*檢定都必須校準到 ~α。
故 outcome 取「急殺窗口『之後』的單日報酬」(非重疊),並加 cooldown 讓事件不黏在
一起——避免 overlapping horizon 的自相關把 SE 灌水(那是 Stage 5 的另一個錯,別在這
裡混進來)。如此唯一灌大假陽性數的就是 variant 數 m 本身。
"""
import sys
from pathlib import Path

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from quant101 import stats as q  # noqa: E402


def run_variants(returns, variants, cooldown=10):
    """每個 (lookback, worst_pct) 變體 -> 一個校準過的 p 值.

    型態:創 lookback 日新高 -> 之後 1..4 天內出現「過去 lookback 最慘 worst_pct」的急殺;
    outcome = 急殺窗口之後那一天的單日報酬;檢定其均值是否異於 0.
    """
    n = len(returns)
    prices = np.exp(np.cumsum(returns))
    pvals = []
    for lookback, worst_pct in variants:
        outcomes, last = [], -10**9
        for t in range(lookback, n - 6):
            if t - last < cooldown:
                continue
            if prices[t] >= prices[t - lookback:t + 1].max():
                thr = np.quantile(returns[t - lookback:t], worst_pct)
                if returns[t + 1:t + 5].min() <= thr:
                    outcomes.append(returns[t + 5])      # 非重疊的單日 outcome
                    last = t
        outcomes = np.array(outcomes)
        if outcomes.size < 5:
            pvals.append(np.nan)
            continue
        _, p = stats.ttest_1samp(outcomes, 0.0)
        pvals.append(p)
    return np.array(pvals)


# 50 個變體:lookback × worst_pct 的格點
lookbacks = [120, 150, 180, 210, 252]
worst_pcts = [0.01, 0.02, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20, 0.25, 0.30]
variants = [(lb, wp) for lb in lookbacks for wp in worst_pcts]
print(f"變體數 m = {len(variants)}")

rng = np.random.default_rng(7)
ret = rng.normal(0, 0.012, size=4000)          # 純噪音:無漂移、無自相關、無訊號
p = run_variants(ret, variants)
p_valid = p[np.isfinite(p)]
n_sig = int((p_valid < 0.05).sum())
print("\n純噪音資料(無任何訊號):")
print(f"  有效檢定數       = {p_valid.size}")
print(f"  raw 顯著 (p<.05) = {n_sig}   (理論期望 ≈ m·α = {p_valid.size*0.05:.1f})")
print(f"  最小 p 值         = {p_valid.min():.4f}  <- 看起來很厲害,純屬運氣")

for name, fn in [("Bonferroni", q.bonferroni), ("Holm", q.holm),
                 ("BH (FDR)", q.benjamini_hochberg)]:
    rej, _ = fn(p_valid, 0.05)
    print(f"  {name:12s} 校正後存活 = {int(rej.sum())}")

# 重複多個 seed:平均顯著比例 ≈ α(證明單一檢定校準正確,假陽性純來自 m)
print("\n重複 40 個 seed,確認單一檢定校準 ≈ α:")
rates = []
for s in range(40):
    ps = run_variants(np.random.default_rng(1000 + s).normal(0, 0.012, 4000), variants)
    ps = ps[np.isfinite(ps)]
    rates.append((ps < 0.05).mean())
print(f"  平均 raw 顯著比例 = {np.mean(rates):.3f}  (理論 α = 0.05 ✓)")
print(f"  => 每次都約 {np.mean(rates)*len(variants):.0f} 個變體『顯著』,"
      "全是運氣;Bonferroni/Holm/BH 校正後幾乎全滅。")
print("\n結論:單一未校正 p 值在『會試很多定義』的世界裡毫無意義——"
      "這就是 garden of forking paths。")
