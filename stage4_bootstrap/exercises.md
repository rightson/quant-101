# Stage 4 習題

參考解在 `solutions/`,皆可執行。

---

## 習題 1 — 9 筆年報酬的 percentile / BCa bootstrap CI vs closed-form

1. 對 9 筆年報酬 `[0.085,-0.12,0.21,-0.05,0.30,-0.017,0.11,-0.23,0.16]` 跑
   percentile 與 BCa bootstrap CI。
2. 與 closed-form t-CI(`quant101.stats.t_ci_mean`)並陳。
3. 交叉驗證:自寫 bootstrap vs `scipy.stats.bootstrap`(percentile 與 bca)。
4. 一句話:三種區間為何都寬到沒用?為什麼**小樣本 bootstrap 反而比 t-CI 窄**
   (anti-conservative),因此不是小樣本萬靈丹?

> 對答案:`python solutions/ex1_bootstrap_ci.py`
> 期望:percentile≈[−5.8%, +15.2%]、BCa≈[−6.2%, +14.8%]、t-CI=[−8.0%, +17.9%];
> 與 scipy 在 MC 誤差內一致。

---

## 習題 2 — permutation test:事件後報酬 vs 隨機同窗報酬

1. 取事件(創新高後急殺)之後的單日報酬,與非事件日的同 offset 報酬。
2. 用 permutation test(打亂標籤)檢定兩者均值差,得 empirical p。
3. 一句話:為什麼在(無動能的)合成資料上看不出差異。

> 對答案:`python solutions/ex2_permutation_test.py`
> 期望:合成資料上 p≈0.3,不顯著。

---

## Notebook 任務(過 gate 前必做)

跑 `notebook_stage4.py`:
- 用 **stationary bootstrap** 對 TAIEX 報酬重抽,跑出型態的 empirical p-value 與 CI;
- 與 Stage 2 的 closed-form t 檢定 p 值**並陳**;
- 展示對 **overlapping 多日報酬**,naive bootstrap CI 比 stationary 版窄好幾倍
  (naive 低估自相關造成的不確定性)。
