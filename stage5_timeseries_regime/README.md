# Stage 5 — Time-Series Analysis 與 Regime

> **修的錯**:錯誤 D(non-stationarity、non-independence、effective sample size 被壓低)。
> **Duration**:5–6 週。**Prereq**:Stage 1(Stage 4 有幫助)。

前面各站的公式默認觀測**獨立、同分布**。這一站把那個假設拆掉:報酬有 autocorrelation、
volatility clustering、以及跨 1999–2026 的 **regime** 變化。三個後果:(1) overlapping
報酬的有效樣本只有約 n/H;(2) σ 是動態的,單一 σ 的 SE 會錯;(3) 那 9~10 個事件多半擠在
同一種 regime,所以「訊號」很可能只是「身處某 regime」的 proxy。

## 四拍節奏
1. **讀**:Tsay, *Analysis of Financial Time Series*;進階 Hamilton(含 1989 Markov-switching);Engle (1982)、Bollerslev (1986)。
2. **算**:跑 `notebook_stage5.py`,用 Markov-switching 切 regime 並檢定事件群聚。
3. **重做 case**:對 TAIEX 配 GARCH、估 effective sample size。
4. **過 gate**:見最下方。

## Milestones
- **M5.1** Strict vs weak stationarity、ergodicity;ACF/PACF;AR/MA/ARMA。
- **M5.2** Autocorrelation 如何壓低 effective sample size。
- **M5.3** Volatility clustering 與 ARCH/GARCH(為何 TAIEX 的 σ 非常數,SE 要小心)。
- **M5.4 核心**:Markov-switching / structural break(形式化「跨不同 regime 不能 pool」)。

## 檔案
| 檔案 | 用途 |
|---|---|
| `lecture.md` | 精講稿 |
| `exercises.md` | 習題 |
| `solutions/ex1_acf_garch.py` | ACF/PACF + GARCH(1,1),展示波動叢聚與動態 σ |
| `solutions/ex2_effective_sample_size.py` | overlapping 報酬的 n_eff≈n/H;事件的有效樣本 < 事件數 |
| `notebook_stage5.py` | **gate 樣板**:Markov-switching 切 regime + 事件群聚檢定 |

共用工具在 `src/quant101/timeseries.py`:`effective_sample_size`、`regime_cluster_test`、
`count_regime_spells`。GARCH 用 `arch`、Markov-switching 用 `statsmodels`。

## Gate
能用 **Markov-switching** 切 regime 並檢定事件是否群聚,給出「此訊號是否為 regime proxy」
的有依據判斷。

> **參考值(已用本 repo 程式驗證,合成資料)**:
> - GARCH(1,1):α≈0.07、β≈0.90、**persistence≈0.97**;conditional vol 年化 ~12%–51%。
> - effective sample:overlapping 20d 報酬 n=7151 → **n_eff≈350**(n/n_eff≈20≈H)。
> - Markov-switching 2-regime:高波動 σ² 約低波動 4×,高波動佔 ~27%,P[stay]≈0.90–0.96。
> - 事件群聚:**82%(18/22)落在高波動 regime vs 基準 27%,binomial p≈1.7e-7**
>   ⇒ 訊號大半是 regime proxy;22 個事件只落在 ~15 個獨立高波動叢集。

**正典**:Tsay, *Analysis of Financial Time Series*;Hamilton, *Time Series Analysis*(1989 Markov-switching);Engle (1982)、Bollerslev (1986)。
