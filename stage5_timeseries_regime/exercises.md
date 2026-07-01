# Stage 5 習題

參考解在 `solutions/`,皆可執行(需要 `arch` 與 `statsmodels`)。

---

## 習題 1 — ACF/PACF + GARCH(1,1):波動叢聚

1. 對 TAIEX 報酬畫/印 ACF、PACF;再對 **報酬²** 畫 ACF。
2. 配 GARCH(1,1),報 α、β 與 persistence α+β;看 conditional volatility 隨時間變。
3. 一句話:為什麼「報酬幾乎不自相關」但「σ 非常數」——以及這對用單一 σ 算 SE 的傷害。

> 對答案:`python solutions/ex1_acf_garch.py`
> 期望:ACF 報酬 ≈ 0(0.01),ACF 報酬² 明顯 > 0(≈0.13);GARCH α≈0.07、β≈0.90、
> persistence≈0.97;conditional vol 年化在 ~12%–51% 間擺盪。

---

## 習題 2 — effective sample size

1. 對日報酬算 n_eff(≈ n,因幾乎不自相關)。
2. 對 **overlapping H 日報酬**(文章式的「後續 N 日報酬」)算 n_eff,展示
   `n/n_eff ≈ H`——自相關把有效樣本壓成約 n/H。
3. 說明「9~10 個聚在循環高點的事件,有效樣本 < 事件數」:用高波動 regime 的
   叢集數當獨立事件的代理。

> 對答案:`python solutions/ex2_effective_sample_size.py`
> 期望:overlapping 20d → n_eff≈350(ratio≈20);22 個事件只落在 ~15 個高波動叢集。

---

## Notebook 任務(過 gate 前必做)

跑 `notebook_stage5.py`:用 2-regime Markov-switching 把 1999–2026 切 regime,檢定型態
事件是否 cluster 在特定 regime,給出「此訊號是否為 regime proxy」的有依據判斷。
