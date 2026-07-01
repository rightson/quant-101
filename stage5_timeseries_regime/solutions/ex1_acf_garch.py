#!/usr/bin/env python3
"""Stage 5 / 習題 1 參考解 — ACF/PACF + GARCH(1,1):波動叢聚.

執行:  python solutions/ex1_acf_garch.py
展示:報酬本身幾乎不自相關,但 |報酬|/報酬² 強自相關(volatility clustering);
GARCH(1,1) 的 conditional volatility 隨時間變,persistence α+β 接近 1。
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from quant101 import data  # noqa: E402
from statsmodels.tsa.stattools import acf, pacf  # noqa: E402

data.build(prefer_real=False)
r = data.daily_returns(kind="simple")
rv = r.to_numpy()
print(f"[data: {'synthetic' if data.is_synthetic() else 'real ^TWII'}]  n={len(rv)}")

# 1) ACF/PACF:報酬 vs 報酬²
a_r = acf(rv, nlags=10, fft=True)
a_r2 = acf(rv**2, nlags=10, fft=True)
p_r = pacf(rv, nlags=10)
print("\nACF  報酬   lag1-5:", np.round(a_r[1:6], 3))
print("PACF 報酬   lag1-5:", np.round(p_r[1:6], 3))
print("ACF  報酬²  lag1-5:", np.round(a_r2[1:6], 3), " <- 明顯 > 0:波動叢聚")
print("=> 報酬近似白噪音(不可預測),但『大波動跟著大波動』——σ 非常數。")

# 2) GARCH(1,1)
from arch import arch_model  # noqa: E402
res = arch_model(rv * 100, mean="Constant", vol="GARCH", p=1, q=1, dist="t").fit(disp="off")
a = res.params["alpha[1]"]; b = res.params["beta[1]"]
print(f"\nGARCH(1,1):  alpha={a:.3f}  beta={b:.3f}  persistence α+β={a+b:.3f}")
cv = res.conditional_volatility
print(f"conditional volatility(年化%):  min={cv.min()*np.sqrt(252):.1f}  "
      f"max={cv.max()*np.sqrt(252):.1f}  ratio={cv.max()/cv.min():.1f}x")
print("=> persistence 接近 1:波動衝擊衰退很慢;σ 在時間上大幅擺盪。")
print("   對判讀的意義:用『全期單一 σ』算的 SE/CI 會錯——σ 本身是動態的(Stage 8 尾部接這條)。")

# optional figure
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 1, figsize=(9, 5), sharex=True)
    idx = data.load_prices().index[1:]
    axes[0].plot(idx, rv, lw=0.4, color="grey"); axes[0].set_ylabel("daily return")
    axes[1].plot(idx, cv * np.sqrt(252), lw=0.8, color="#C44E52")
    axes[1].set_ylabel("GARCH cond. vol (ann.)"); axes[1].set_xlabel("date")
    axes[0].set_title("returns look white; volatility clusters (GARCH conditional σ)")
    out = Path(__file__).resolve().parents[2] / "figures"; out.mkdir(exist_ok=True)
    fig.tight_layout(); fig.savefig(out / "stage5_garch_volatility.png", dpi=110)
    print(f"\nsaved figure -> {out/'stage5_garch_volatility.png'}")
except Exception as exc:
    print(f"(figure skipped: {exc})")
