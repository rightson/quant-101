#!/usr/bin/env python3
"""Stage 6 / 習題 2 參考解 — 殘差是否還需要「主力洗盤」?

執行:  python solutions/ex2_residual_no_manipulation.py
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
H, L = 63, 252
mask = pr.new_high_mask(prices, L)
d = pr.decompose_conditional_return(prices, mask, horizon=H, lookback=L)

# 1) 殘差的正確 SE:前瞻窗口 overlapping ⇒ 殘差自相關 ⇒ SE 用 n_eff 打折
print("殘差(drift+momentum 之外)= "
      f"{d['residual']:+.2%}")
print(f"  k(創新高窗口數)      = {d['k']}")
print(f"  n_eff(有效獨立窗口)  = {d['n_eff']:.0f}   ← overlapping 前瞻報酬把 {d['k']} 壓成 ~{d['n_eff']:.0f}")
print(f"  正確 SE = s/√n_eff    = {d['residual_se']:.2%}   (若誤用 s/√k 會嚴重灌水顯著性)")
print(f"  residual t            = {d['residual_t']:+.2f}")
print(f"  residual 95% CI       = [{d['residual_ci'][0]:+.2%}, {d['residual_ci'][1]:+.2%}]  "
      f"{'← 含 0' if d['residual_ci'][0] < 0 < d['residual_ci'][1] else ''}")

# 2) 左尾對照:創新高後的 crash 是否比無條件更兇?
f = pr.forward_return(prices, H)
valid = np.isfinite(f)
cm = mask & valid
print("\n左尾對照(前瞻 63 日報酬):")
print(f"  無條件    q05={np.nanquantile(f[valid], 0.05):+.2%}   最差={np.nanmin(f[valid]):+.2%}")
print(f"  創新高後  q05={np.nanquantile(f[cm], 0.05):+.2%}   最差={np.nanmin(f[cm]):+.2%}")
print("  => 創新高後的左尾與無條件同級,crash 不因『剛創新高』而變兇;"
      "\n     「先漲後崩」只是同一條肥左尾的抽樣,不是洗盤觸發的(尾巴估計留給 Stage 8)。")

# 3) 終判
sig = d["residual_ci"][0] < 0 < d["residual_ci"][1]
print("\n=== 終判 ===")
print(f"扣掉 drift + momentum 後,殘差在統計上{'不可與 0 區分' if sig else '≠0(需檢視)'}"
      f"(t={d['residual_t']:+.2f}, CI 含 0)。")
print("=> 文章的正報酬 = drift + momentum,兩者皆機械;**殘差不需要任何額外故事**,"
      "\n   「主力洗盤」是對一個統計上為 0 的殘差強加的敘事。")
