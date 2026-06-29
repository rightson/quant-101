#!/usr/bin/env python3
"""Stage 2 / 習題 2 參考解 — power analysis for the −1.7% vs +8.5% claim.

執行:  python solutions/ex2_power_analysis.py
交叉驗證:自寫的 non-central t power  vs  statsmodels TTestPower.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from quant101 import stats as q  # noqa: E402

# 1) effect size
mean_diff = 0.085 - (-0.017)        # +8.5% vs −1.7% = 10.2pp
sigma = 0.22                        # annual TAIEX-scale return sd
d = mean_diff / sigma
print(f"mean diff = {mean_diff:.3%},  σ = {sigma:.0%},  Cohen's d = {d:.4f}")

# 2) power at n=9 (one-sample t, two-sided, α=0.05)
pw9 = q.power_one_sample_t(d, n=9)
print(f"power(n=9)  = {pw9:.4f}   -> {'< 0.3 ✓' if pw9 < 0.3 else 'NOT < 0.3'}")

# 3) n required for power 0.8
n80 = q.n_for_power_one_sample_t(d, power=0.8)
print(f"n for power=0.8 = {n80}")

# cross-check with statsmodels (if available)
try:
    from statsmodels.stats.power import TTestPower
    tp = TTestPower()
    pw9_sm = tp.power(effect_size=d, nobs=9, alpha=0.05, alternative="two-sided")
    n_sm = tp.solve_power(effect_size=d, power=0.8, alpha=0.05, alternative="two-sided")
    print(f"\n[statsmodels] power(n=9)={pw9_sm:.4f}, n(power=.8)={np.ceil(n_sm):.0f}")
except Exception as exc:
    print(f"(statsmodels cross-check skipped: {exc})")

print(
    "\n判讀:即使『先出場較好』這個效果真的存在,n=9 也只有 ~23% 機率偵測到。\n"
    "所以『回測沒看到顯著差異』不是『沒有差異』的證據——是 power 根本不夠。\n"
    "要可靠偵測這個大小的效果,需要約 39 次「獨立」事件(文章只有 9 次,且相關)。"
)
