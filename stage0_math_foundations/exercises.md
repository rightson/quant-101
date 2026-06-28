# Stage 0 習題

參考解在 `solutions/`,每份都可執行(`python solutions/xxx.py`)。先自己做再對答案。

---

## 習題 1 — 徒手 joint → marginal / conditional / 全期望

給定二維離散 joint table(`X`=是否創新高,`Y`=之後 20 日報酬分桶):

| | Y = −10% | Y = 0% | Y = +10% | (列和) |
|---|---|---|---|---|
| **X = 0(沒創新高)** | 0.20 | 0.30 | 0.10 | 0.60 |
| **X = 1(創新高)** | 0.05 | 0.15 | 0.20 | 0.40 |

請手算:
1. 兩個 marginal:`P(X)` 與 `P(Y)`。
2. 條件分布 `P(Y | X=1)` 與 `P(Y | X=0)`。
3. `E[Y | X=1]`、`E[Y | X=0]`、`E[Y]`。
4. **驗證 law of total expectation**:`E[Y] = E[Y|X=1]P(X=1) + E[Y|X=0]P(X=0)`。
5. 一句話:這裡 `E[Y|X=1] - E[Y]` 為什麼是正的?它需要「主力」來解釋嗎?

> 對答案:`python solutions/ex1_total_expectation.py`

---

## 習題 2 — 用 projection 解釋「OLS 係數 = 把 Y 投影到 X 張成的空間」

1. 寫出 `β̂ = argmin ‖Y - Xβ‖²` 的一階條件,並導出 `β̂ = (XᵀX)⁻¹XᵀY`。
2. 說明 `Ŷ = Xβ̂ = HY` 為什麼是 `Y` 在 `col(X)` 上的正交投影:
   - 殘差 `e = Y - Ŷ` 與 `col(X)` 正交(`Xᵀe = 0`);
   - `H` 是投影矩陣(`H²=H`、`Hᵀ=H`)。
3. **數值驗證**:隨機生一組 `(X, Y)`,分別用 (a) closed-form、(b) `numpy.linalg.lstsq`、
   (c) 手動投影 `H=X(XᵀX)⁻¹Xᵀ` 三種方式算 `Ŷ`,確認三者相同,且 `Xᵀe ≈ 0`。

> 對答案:`python solutions/ex2_ols_projection.py`

---

## Notebook 任務(過 gate 前必做)

跑 `notebook_conditioning.py`:模擬 `X=是否創新高`、`Y=後續報酬` 的 joint 分布,
**數值上**展示 `E[Y|X=創新高] ≠ E[Y]`,並用一句話說清楚這就是「對創新高 conditioning
= 對 positive momentum conditioning」。
