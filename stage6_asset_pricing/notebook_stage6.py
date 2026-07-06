# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
# ---

# %% [markdown]
# # Stage 6 Notebook — 把「創新高後 +4.7%」拆成 drift + momentum(gate)
#
# 主張:文章的正報酬**不是 edge**,是兩個機械項相加——股市**向上 drift** + 「創新高」所
# conditioning 的 **momentum premium**。把這兩塊減掉,殘差在統計上是 **0**:**沒有東西留給
# 「主力洗盤」去解釋**。同一序列的偶發 crash 只是肥左尾,不因創新高而變兇(接 Stage 8)。
#
# 跑法:`python notebook_stage6.py`(圖存到 figures/;需要 statsmodels)。

# %%
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from quant101 import data, pricing as pr  # noqa: E402

data.build(prefer_real=False)
prices = data.load_prices()["close"].to_numpy()
r = data.daily_returns(kind="simple").to_numpy()
n = len(prices)
H, L = 63, 252  # 前瞻 3 個月;動能訊號用過去 1 年
print(f"[data: {'synthetic' if data.is_synthetic() else 'real ^TWII'}]  n={n}")

# %% [markdown]
# ## 1. Market model 機制驗證(M6.2,Stage 7 的 abnormal return 從這讀)
#
# `r_i = α + β·r_market + ε`。植入 α=0、β=1.2 的合成資產,迴歸應把 β̂≈1.2、α̂≈0 抓回來。
# 抓得回來 ⇒ Stage 7 拿它產 abnormal return 是可靠的。

# %%
asset = pr.make_beta_asset(r, alpha_daily=0.0, beta=1.2, idio_vol=0.008, seed=607)
mm = pr.market_model(asset, r)
print(f"植入 α=0, β=1.2  →  α̂={mm['alpha']:+.5f} (t={mm['t_alpha']:+.2f}, ≈0)  "
      f"β̂={mm['beta']:.3f} (t={mm['t_beta']:.0f})  R²={mm['r2']:.2f}")
print("abnormal return AR_t = r_i − (α̂ + β̂·r_m) = 迴歸殘差;Stage 7 把事件窗口的 AR 累成 CAR/BHAR。")

# %% [markdown]
# ## 2. 「創新高」= 對 positive momentum conditioning
#
# 先確認 time-series momentum 存在(TSMOM 迴歸 b>0),再看創新高日的 trailing 報酬遠高於全期。

# %%
s = pr.trailing_return(prices, L)
f = pr.forward_return(prices, H)
reg = pr.tsmom_regression(s, f)
mask = pr.new_high_mask(prices, L)
print(f"TSMOM 迴歸 r_fwd ~ a + b·r_trailing:  b={reg['b']:+.4f}  t_b={reg['t_b']:+.2f}")
d = pr.decompose_conditional_return(prices, mask, horizon=H, lookback=L)
print(f"創 {L} 日新高日 k={d['k']}:平均 trailing 報酬 {d['trailing_mean_cond']:+.1%} "
      f"≫ 全期 {d['trailing_mean']:+.1%}  ⇒ 創新高 ≈ top-momentum")

# %% [markdown]
# ## 3. 分解:conditional = drift + momentum + residual
#
# 兩條 OLS 恆等式:`a+b·s̄ = f̄ = drift`;`momentum = b·(s̄_cond − s̄)`;
# `residual = f̄_cond − (drift+momentum)` = 創新高日的迴歸殘差平均。

# %%
print(f"conditional 前瞻報酬  = {d['conditional_return']:+.2%}")
print(f"  ├─ drift(無條件)     = {d['drift']:+.2%}")
print(f"  ├─ momentum premium   = {d['momentum_premium']:+.2%}")
print(f"  └─ residual           = {d['residual']:+.2%}")

# %% [markdown]
# ## 4. 殘差檢定:SE 必須用 n_eff 打折(接 Stage 5)
#
# 前瞻窗口 overlapping ⇒ 殘差自相關 ⇒ 用 `s/√k` 會灌水。改用 Stage 5 的
# `effective_sample_size`:`s/√n_eff`。

# %%
print(f"k={d['k']} 個 overlapping 窗口只值 n_eff≈{d['n_eff']:.0f} 個獨立觀測")
print(f"residual SE = {d['residual_se']:.2%}   t = {d['residual_t']:+.2f}   "
      f"95% CI = [{d['residual_ci'][0]:+.2%}, {d['residual_ci'][1]:+.2%}]")
insig = d["residual_ci"][0] < 0 < d["residual_ci"][1]
print(f"=> 殘差{'統計上不可與 0 區分(CI 含 0)' if insig else '≠0,需檢視'}。")

# %% [markdown]
# ## 5. 左尾對照:「先漲後崩」= 肥左尾,不是洗盤
# %%
valid = np.isfinite(f)
cm = mask & valid
print("前瞻 63 日報酬左尾:")
print(f"  無條件    q05={np.nanquantile(f[valid],0.05):+.2%}  最差={np.nanmin(f[valid]):+.2%}")
print(f"  創新高後  q05={np.nanquantile(f[cm],0.05):+.2%}  最差={np.nanmin(f[cm]):+.2%}")
print("=> crash 不因創新高而變兇;偶發急殺只是同一條肥左尾(尾巴估計 → Stage 8)。")

# %% [markdown]
# ## 6. 對照面板:當 momentum 真的存在時(植入真動能序列)
#
# 合成 TAIEX 是隨機漫步(無真動能),故上面 momentum≈0、前瞻報酬幾乎全是 drift。用
# `make_momentum_series` 造一條帶持續趨勢的序列,對 top-tercile 動能 conditioning,看機器
# 是否把該漲的正確歸給 momentum、殘差仍為 0。

# %%
mp, _ = pr.make_momentum_series(n, seed=606, rho=0.97, trend_vol=0.0015, noise_vol=0.010)
sm = pr.trailing_return(mp, L)
mask2 = sm >= np.nanquantile(sm, 2 / 3)
d2 = pr.decompose_conditional_return(mp, mask2, horizon=H, lookback=L)
print(f"[植入真動能] top-tercile 動能, k={d2['k']}:")
print(f"  conditional {d2['conditional_return']:+.2%} = drift {d2['drift']:+.2%} + "
      f"momentum {d2['momentum_premium']:+.2%} (t_b={d2['t_b']:.1f}) + residual {d2['residual']:+.2%} "
      f"(t={d2['residual_t']:+.2f})")
print("  => momentum 真存在時,機器正確歸因,殘差仍≈0。「有 signal」不等於「需要洗盤」。")

# %% [markdown]
# ## 7. 圖:conditional 報酬的 waterfall 分解
# %%
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = ["drift", "momentum", "residual", "= conditional"]
    vals = [d["drift"], d["momentum_premium"], d["residual"], d["conditional_return"]]
    fig, ax = plt.subplots(figsize=(8, 4))
    cum = 0.0
    for i, (lab, v) in enumerate(zip(labels[:-1], vals[:-1])):
        ax.bar(i, v, bottom=cum, color=["#4C72B0", "#55A868", "#C44E52"][i], alpha=0.85)
        ax.text(i, cum + v + 0.001, f"{v:+.2%}", ha="center", fontsize=9)
        cum += v
    ax.bar(3, d["conditional_return"], color="black", alpha=0.7)
    ax.text(3, d["conditional_return"] + 0.001, f"{d['conditional_return']:+.2%}", ha="center", fontsize=9)
    ax.axhline(0, color="grey", lw=0.6)
    ax.set_xticks(range(4)); ax.set_xticklabels(labels)
    ax.set(title=f"new-high forward-{H}d return = drift + momentum + residual "
                 f"(residual t={d['residual_t']:+.2f}, CI 含 0)",
           ylabel="cumulative return")
    o = Path(__file__).resolve().parents[1] / "figures"; o.mkdir(exist_ok=True)
    fig.tight_layout(); fig.savefig(o / "stage6_drift_momentum.png", dpi=120)
    print(f"saved -> {o/'stage6_drift_momentum.png'}")
except Exception as exc:
    print(f"(figure skipped: {exc})")

# %% [markdown]
# ## 8. 過 gate 的判斷
# - **market model** 機制正確(β̂≈1.21、R²≈0.75)⇒ Stage 7 的 abnormal return 可靠。
# - 「創新高」≈ 對 **positive momentum** conditioning;文章的正報酬 = **drift + momentum**,兩者皆機械。
# - 扣掉這兩塊,**殘差用 n_eff 校正後統計上為 0(CI 含 0)**⇒ **殘差不需要任何額外故事**;
#   「主力洗盤」是對一個 0 殘差強加的敘事。
# - 「先漲後崩」的 crash **不因創新高而變兇**,只是同一條肥左尾——接 Stage 8。
# - **注意**:本合成序列無真動能,故前瞻報酬幾乎全是 drift;§6 在植入真動能的序列上示範
#   momentum 項為正時的正確歸因。真實 `^TWII`:`python data/build_dataset.py`。
