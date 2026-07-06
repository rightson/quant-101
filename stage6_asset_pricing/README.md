# Stage 6 — Empirical Asset Pricing(Factor / Momentum / Mean Reversion)

> **修的錯**:錯誤 E(沒認出 +4.7% 是 momentum 的機械結果);「先漲後反轉」為何是
> 「drift + 偶發 crash」的自然形狀,不需要「主力洗盤」敘事。
> **Duration**:4–5 週。**Prereq**:Stage 0–2;Stage 5 有幫助。

前五站都在問「這個數字是 signal 還是 noise?」。這一站換個問法:**就算它是 signal,
它是不是早就有名字了?**「創新高後前瞻報酬為正」不需要任何 edge——它是兩個教科書等級
機械項的加總:(1) 股市長期**向上 drift**;(2) 「創新高」本質是 conditioning 在
**positive momentum**,而 momentum premium 是有據可查的 factor。把這兩塊減掉,殘差在
統計上是 0——**沒有東西留給「洗盤」去解釋**。

## 四拍節奏
1. **讀**:Campbell, Lo & MacKinlay, *The Econometrics of Financial Markets*;Jegadeesh & Titman (1993);Moskowitz, Ooi & Pedersen (2012);Fama & French (1993)。
2. **算**:跑 `notebook_stage6.py`,把「創新高後 H 日報酬」拆成 drift + momentum + residual。
3. **重做 case**:回到文章的 +4.7%,證明它 = drift + momentum,殘差不顯著。
4. **過 gate**:見最下方。

## Milestones
- **M6.1** EMH 與 joint hypothesis problem(任何「異常報酬」都是「模型 × 效率」的聯合檢定)。
- **M6.2** CAPM 與 market model:`r = α + β·r_market + ε`(Stage 7 event study 的 abnormal return 從這讀)。
- **M6.3** Fama-French 3/5 factor、Carhart momentum:報酬的橫斷面由少數 factor 解釋。
- **M6.4 核心**:time-series momentum 與 cross-sectional momentum;long-horizon mean reversion;「先漲後反轉」為何是 drift + 左尾的自然形狀。

## 檔案
| 檔案 | 用途 |
|---|---|
| `lecture.md` | 精講稿 |
| `exercises.md` | 習題 |
| `solutions/ex1_drift_momentum_decomposition.py` | 把創新高後前瞻報酬拆成 drift + momentum + residual |
| `solutions/ex2_residual_no_manipulation.py` | 殘差的 n_eff-校正檢定 + 左尾對照:殘差 = 0,crash 不因創新高而變兇 |
| `notebook_stage6.py` | **gate 樣板**:decomposition + market-model 機制 + momentum 對照面板 |

共用工具在 `src/quant101/pricing.py`:`market_model`、`tsmom_regression`、
`decompose_conditional_return`(殘差 SE 用 Stage 5 的 `effective_sample_size` 打折,
因 overlapping H 日報酬自相關)、`forward_return`/`trailing_return`/`new_high_mask`、
以及可重現的 `make_momentum_series`/`make_beta_asset`。回歸用 `statsmodels`。

## Gate
能把文章「創新高後 +4.7%」拆成 **drift + momentum**,並說明**殘差是否還需要額外故事**。

> **參考值(已用本 repo 程式驗證,合成資料)**:
> - **Market model**(植入 α=0、β=1.2):α̂≈0(t≈−2.5)、**β̂≈1.21(t≈145)、R²≈0.75**
>   ⇒ abnormal return 的機制正確,Stage 7 直接接。
> - **Gate 拆解**(TAIEX 合成、創 252 日新高、H=63 日、k=342):
>   conditional=**+0.28%** = drift **+1.52%** + momentum **+0.37%**(b>0, t_b≈3.4)
>   + residual **−1.61%**;殘差 SE 用 **n_eff≈45**(342 個 overlapping 窗口只值 ~45 個獨立)
>   ⇒ **residual t≈−1.4、95% CI=[−3.9%, +0.7%] 含 0** ⇒ **殘差統計上是 0,不需任何額外故事**。
>   在此隨機漫步-帶-drift 的合成序列上,前瞻報酬幾乎**全是 drift**;momentum 也不需要,更遑論洗盤。
> - **左尾對照**:創新高後 63 日報酬的 5% 分位 −14.5%、最差 −24%,與**無條件**的 −12.6%/−27%
>   同級 ⇒ 「先漲後反轉」的 crash **不因創新高而變兇**,只是同一條肥左尾(接 Stage 8)。
> - **Momentum 對照面板**(植入真動能序列、top-tercile 動能、H=63):conditional=**+7.62%**
>   = drift **+4.77%** + momentum **+2.16%**(b>0, t_b≈6.3)+ residual **+0.69%(t≈0.1,不顯著)**
>   ⇒ 當 momentum 真的存在時,decomposition 機器正確把它歸給 momentum,殘差仍是 0。

**正典**:Campbell, Lo & MacKinlay, *The Econometrics of Financial Markets*;Jegadeesh & Titman (1993);Moskowitz, Ooi & Pedersen (2012);Fama & French (1993)。
