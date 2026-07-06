# Stage 6 習題

參考解在 `solutions/`,皆可執行(需要 `statsmodels`)。

---

## 習題 1 — 把「創新高後 3 個月」報酬拆成 drift + momentum

1. 定 `r_fwd` = 未來 63 日(≈3 個月)報酬、`r_trailing` = 過去 252 日報酬,配
   time-series momentum 迴歸 `r_fwd ~ a + b·r_trailing`,確認 **b>0**(動能存在)。
2. 用兩條 OLS 恆等式把「創 252 日新高那些日子」的前瞻報酬拆成
   **drift + momentum premium + residual**(drift = 無條件均值;momentum = `b·(s̄_cond−s̄)`)。
3. 一句話:為什麼「對創新高 conditioning」本質上就是「對 positive momentum conditioning」。

> 對答案:`python solutions/ex1_drift_momentum_decomposition.py`
> 期望(合成資料、H=63、k=342):conditional≈+0.28% = drift +1.52% + momentum +0.37%
> + residual −1.61%;b>0(t_b≈3.4)。在此隨機漫步序列上前瞻報酬幾乎全是 drift。
> 另在**植入真動能**的對照序列上:conditional +7.62% = drift +4.77% + momentum +2.16%
> + residual +0.69%,示範 momentum 項為正時機器如何正確歸因。

---

## 習題 2 — 論證殘差是否還需要「主力洗盤」

1. 對習題 1 的殘差算**正確的 SE**:前瞻窗口 overlapping、殘差自相關,SE 必須用 Stage 5 的
   `effective_sample_size` 打折(`s/√n_eff`,非 `s/√k`)。報 residual 的 t 與 95% CI。
2. **左尾對照**:比較「創新高後 63 日報酬」與「無條件 63 日報酬」的 5% 分位與最差值,說明
   「先漲後崩」的 crash 是否因創新高而變兇。
3. 一句話終判:扣掉 drift + momentum 後,殘差在統計上是否 ≠ 0?還需不需要額外故事?

> 對答案:`python solutions/ex2_residual_no_manipulation.py`
> 期望:n_eff≈45(342 個窗口只值 ~45 獨立);residual t≈−1.4、95% CI≈[−3.9%,+0.7%] **含 0**
> ⇒ 殘差統計上是 0。創新高後左尾(q05≈−14.5%)與無條件(≈−12.6%)同級 ⇒ crash 不變兇。
> **終判:不需要任何洗盤故事。**

---

## Notebook 任務(過 gate 前必做)

跑 `notebook_stage6.py`:
1. 驗 market model 機制(植入 α/β → 抓回 β̂≈1.21、R²≈0.75,Stage 7 要用)。
2. 把「創新高後 H 日報酬」拆成 drift + momentum + residual,並用 n_eff-校正檢定殘差。
3. 對照面板:在植入真動能的序列上示範 momentum 項為正、殘差仍為 0。
4. 給出 gate 判斷:文章 +4.7% = drift + momentum,殘差不需額外故事。
