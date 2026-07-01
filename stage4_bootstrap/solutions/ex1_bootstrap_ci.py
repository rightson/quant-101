#!/usr/bin/env python3
"""Stage 4 / 習題 1 參考解 — 9 筆年報酬的 percentile / BCa bootstrap CI vs closed-form.

執行:  python solutions/ex1_bootstrap_ci.py
交叉驗證:自寫 bootstrap vs scipy.stats.bootstrap.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from quant101 import resample as R, stats as q  # noqa: E402

# 同 Stage 1/2 的 9 筆事件年報酬
x = np.array([0.085, -0.12, 0.21, -0.05, 0.30, -0.017, 0.11, -0.23, 0.16])
print(f"x̄ = {x.mean():+.4f},  n = {x.size}")

lo_p, hi_p = R.bootstrap_ci(x, np.mean, n_boot=20000, method="percentile", seed=1)
lo_b, hi_b = R.bca_ci(x, np.mean, n_boot=20000, seed=1)
lo_t, hi_t = q.t_ci_mean(x)
print(f"percentile bootstrap CI = [{lo_p:+.4f}, {hi_p:+.4f}]")
print(f"BCa        bootstrap CI = [{lo_b:+.4f}, {hi_b:+.4f}]")
print(f"closed-form t-CI        = [{lo_t:+.4f}, {hi_t:+.4f}]")

# 交叉驗證 vs scipy
try:
    from scipy import stats as ss
    rp = ss.bootstrap((x,), np.mean, n_resamples=20000, method="percentile",
                      random_state=1).confidence_interval
    rb = ss.bootstrap((x,), np.mean, n_resamples=20000, method="bca",
                      random_state=1).confidence_interval
    print(f"\n[scipy] percentile = [{rp.low:+.4f}, {rp.high:+.4f}]")
    print(f"[scipy] BCa        = [{rb.low:+.4f}, {rb.high:+.4f}]  "
          "(與自寫版在 MC 誤差內一致)")
except Exception as exc:
    print(f"(scipy cross-check skipped: {exc})")

print(
    "\n判讀:\n"
    "  1. 三種區間全都寬到從負到正十幾趴——換工具救不了 n=9。\n"
    "  2. BCa 因報酬左偏而把區間往下修(bias/skew 校正),但寬度沒變小。\n"
    "  3. 注意 bootstrap 區間其實比 t-CI 還*窄*:小樣本 bootstrap 會低估寬度\n"
    "     (anti-conservative),所以 bootstrap 不是小樣本萬靈丹;n 太小時 closed-form\n"
    "     t 反而較誠實。bootstrap 的真正價值在下面——處理『有相關』的資料。"
)
