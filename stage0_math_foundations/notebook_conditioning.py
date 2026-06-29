# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
# ---

# %% [markdown]
# # Stage 0 Notebook — Conditioning on 創新高 = conditioning on momentum
#
# 目標:用模擬 + TAIEX 序列,**數值上**展示
# `E[Y | X=創新高] ≠ E[Y]`,並看清這只是 conditioning 挑了動能為正的子母體。
#
# 跑法:`python notebook_conditioning.py`  或  `jupytext --to ipynb` 後在 Jupyter 跑。

# %%
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from quant101 import data  # noqa: E402

rng = np.random.default_rng(0)

# %% [markdown]
# ## 1. 玩具模型:先把機制講清楚
#
# 造一個有「動能」的序列:`r_t = ρ·r_{t-1} + ε_t`。
# 定義 `X_t = 1{r_t 為過去一年最大}`(創新高代理),`Y_t = r_{t+1}`(下一步報酬)。
# 因為 ρ>0,創新高(近期報酬大)會與未來報酬正相關——這就是 momentum。

# %%
T = 200_000
rho = 0.10
eps = rng.normal(scale=1.0, size=T)
r = np.empty(T)
r[0] = eps[0]
for t in range(1, T):
    r[t] = rho * r[t - 1] + eps[t]

r = pd.Series(r)
roll_max = r.rolling(252).max()
X = (r >= roll_max).astype(int)          # 是否創 252 日新高
Y = r.shift(-1)                          # 後一步報酬
df = pd.DataFrame({"X": X, "Y": Y}).dropna()

E_Y = df["Y"].mean()
E_Y_given_high = df.loc[df["X"] == 1, "Y"].mean()
E_Y_given_not = df.loc[df["X"] == 0, "Y"].mean()
print(f"E[Y]            = {E_Y:+.4f}")
print(f"E[Y|創新高]     = {E_Y_given_high:+.4f}")
print(f"E[Y|沒創新高]   = {E_Y_given_not:+.4f}")
print(f"差 (條件 - 無條件) = {E_Y_given_high - E_Y:+.4f}")

# %% [markdown]
# ↑ 條件期望明顯高於無條件期望——純粹因為 ρ>0(有動能)。
# 現在把動能關掉(ρ=0),差距應該消失(獨立 ⟹ conditioning 無效)。

# %%
eps2 = rng.normal(scale=1.0, size=T)      # ρ=0: 純 i.i.d.
r0 = pd.Series(eps2)
X0 = (r0 >= r0.rolling(252).max()).astype(int)
Y0 = r0.shift(-1)
d0 = pd.DataFrame({"X": X0, "Y": Y0}).dropna()
hi = d0.loc[d0.X == 1, "Y"]
gap0 = hi.mean() - d0.Y.mean()
se0 = hi.std() / np.sqrt(len(hi))         # 創新高樣本數不多 -> 條件均值會抖(Stage 1 主題)
print(f"ρ=0:  E[Y|創新高] - E[Y] = {gap0:+.4f}  "
      f"(n_創新高={len(hi)}, SE≈{se0:.4f} ⟹ 與 0 無異)")

# %% [markdown]
# **結論**:`E[Y|創新高] ≠ E[Y]` 的大小由「創新高 vs 未來報酬」的相關度決定。
# 有動能(ρ>0)→ 明顯正差距;無動能(ρ=0)→ 差距落在抽樣誤差內、與 0 無異。
# 注意 ρ=0 那個 −0.02 不是「動能」,它只是少數創新高日的條件均值抖動——
# 這正是 Stage 1 要量化的東西:條件均值自己是個會抖的估計量。

# %% [markdown]
# ## 2. 接到貫穿 case:TAIEX
#
# 同樣的操作搬到(合成或真實的)TAIEX 報酬序列上。
#
# **注意 source**:預設的合成序列**沒有內建動能**(報酬近似 martingale + GARCH 波動),
# 所以這裡的條件差會落在抽樣誤差內、甚至為負——正好印證「無相關 ⟹ conditioning 無效」。
# 換成真實 `^TWII`(`python data/build_dataset.py` 在有網路時)後,因為市場真的有動能,
# 這個條件差通常會翻成正的。**sign 取決於資料裡到底有沒有動能,不是取決於敘事。**

# %%
src = "synthetic" if data.is_synthetic() else "real ^TWII"
print(f"[data source: {src}]")
ret = data.daily_returns(kind="simple")
fwd20 = ret.rolling(20).sum().shift(-20)            # 之後 20 個交易日累積報酬
close = data.load_prices()["close"]
is_high = (close >= close.rolling(252).max())

tbl = pd.DataFrame({"X": is_high.astype(int), "Y": fwd20}).dropna()
m_uncond = tbl["Y"].mean()
m_cond = tbl.loc[tbl["X"] == 1, "Y"].mean()
print(f"TAIEX  E[fwd20]            = {m_uncond:+.4%}")
print(f"TAIEX  E[fwd20 | 創新高]   = {m_cond:+.4%}")
print(f"TAIEX  差                  = {m_cond - m_uncond:+.4%}")

# %% [markdown]
# ## 3. 一句話(過 gate 用)
#
# > 創新高是「近期報酬為正且大」的指示函數,所以 `E[未來報酬 | 創新高]` 是在對
# > 「動能為正」取條件期望。它跟無條件 `E[未來報酬]` 不同,只因為我們挑了母體裡
# > 動能為正的那一塊——這是 conditioning 的機械結果,不需要「主力」敘事。
#
# 下一站(Stage 1):就算這個差在樣本裡是正的,只有 9 筆時那個正號有多可信?
