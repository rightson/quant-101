#!/usr/bin/env python3
"""Stage 6 / 習題 1 參考解 — 把「創新高後 3 個月」拆成 drift + momentum.

執行:  python solutions/ex1_drift_momentum_decomposition.py
"""
import sys
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from quant101 import data, pricing as pr  # noqa: E402

data.build(prefer_real=False)
prices = data.load_prices()["close"].to_numpy()
n = len(prices)
H, L = 63, 252  # 前瞻 3 個月;動能訊號用過去 1 年
print(f"[data: {'synthetic' if data.is_synthetic() else 'real ^TWII'}]  n={n}")

# 1) time-series momentum 迴歸:r_fwd ~ a + b·r_trailing,確認 b>0
s = pr.trailing_return(prices, L)
f = pr.forward_return(prices, H)
reg = pr.tsmom_regression(s, f)
print(f"\nTSMOM 迴歸 r_fwd ~ a + b·r_trailing:  b={reg['b']:+.4f}  t_b={reg['t_b']:+.2f}  "
      f"(b>0 ⇒ 動能存在,過去漲的未來平均也漲)")

# 2) 把「創 252 日新高」那些日子的前瞻報酬拆成 drift + momentum + residual
mask = pr.new_high_mask(prices, L)
d = pr.decompose_conditional_return(prices, mask, horizon=H, lookback=L)
print(f"\n創 {L} 日新高的日子 k={d['k']}(這些日子的平均 trailing 報酬 "
      f"{d['trailing_mean_cond']:+.1%} ≫ 全期 {d['trailing_mean']:+.1%})")
print(f"  conditional 前瞻報酬  = {d['conditional_return']:+.2%}")
print(f"  ├─ drift(無條件)     = {d['drift']:+.2%}")
print(f"  ├─ momentum premium   = {d['momentum_premium']:+.2%}   = b·(s̄_cond − s̄)")
print(f"  └─ residual           = {d['residual']:+.2%}   (drift+momentum 解釋不了的)")

# 3) 為什麼「conditioning 創新高」= 「conditioning positive momentum」
print("\n=> 一支剛創 252 日新高的標的,trailing 12 個月報酬必然很高;所以「對創新高"
      "\n   conditioning」本質上就是「對 top-momentum conditioning」。正報酬有一塊是"
      "\n   momentum premium 的機械結果,不是 edge。")
if data.is_synthetic():
    print("   本合成序列是隨機漫步 + 正 drift(無真動能),故前瞻報酬幾乎全是 drift;"
          "\n   momentum 也不需要。真實 ^TWII 上 momentum 會是實打實的 factor 酬勞。")

# 對照:植入真動能的序列上,momentum 項會是明確的正數
mp, _ = pr.make_momentum_series(n, seed=606, rho=0.97, trend_vol=0.0015, noise_vol=0.010)
sm = pr.trailing_return(mp, L)
mask2 = sm >= np.nanquantile(sm, 2 / 3)  # top-tercile 動能(留在迴歸支撐內)
d2 = pr.decompose_conditional_return(mp, mask2, horizon=H, lookback=L)
print(f"\n[對照:植入真動能序列,top-tercile 動能,H={H}]")
print(f"  conditional {d2['conditional_return']:+.2%} = drift {d2['drift']:+.2%} + "
      f"momentum {d2['momentum_premium']:+.2%} (t_b={d2['t_b']:.1f}) + residual {d2['residual']:+.2%}")
print("  => momentum 真的存在時,機器把它正確歸給 momentum,殘差仍≈0。")
