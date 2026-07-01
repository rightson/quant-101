# Stage 4 — Bootstrap 與 Resampling

> **修的錯**:之後驗證的主力工具;「嚴謹版」第三點。
> **Duration**:3–4 週。**Prereq**:Stage 2(Stage 4 有幫助但非必需 Stage 3)。

Stage 2 給你 closed-form 的 CI 與 power。但現實裡統計量常常沒有漂亮的解析分布,而且
金融報酬**有自相關**,closed-form 的 `s/√n` 會低估不確定性。這一站給你之後所有驗證的
主力工具:**bootstrap**(讓 sampling distribution 自己長出來)與 **stationary
bootstrap**(尊重報酬的相依結構)。

## 四拍節奏
1. **讀**:Efron & Tibshirani, *An Introduction to the Bootstrap*;Politis & Romano (1994) "The Stationary Bootstrap"。
2. **算**:跑 `notebook_stage4.py`,用 stationary bootstrap 跑出型態的 empirical p-value。
3. **重做 case**:對文章 9 筆年報酬跑 percentile/BCa CI;對事件後報酬跑 permutation test。
4. **過 gate**:見最下方。

## Milestones
- **M4.1** Nonparametric bootstrap;percentile vs BCa CI。
- **M4.2** Permutation test 與 Monte Carlo。
- **M4.3 核心**:block bootstrap 與 stationary bootstrap——報酬有 autocorrelation,naive bootstrap 會低估 SE。

## 檔案
| 檔案 | 用途 |
|---|---|
| `lecture.md` | 精講稿 |
| `exercises.md` | 習題 |
| `solutions/ex1_bootstrap_ci.py` | 9 筆年報酬的 percentile/BCa CI vs closed-form,交叉驗證 scipy |
| `solutions/ex2_permutation_test.py` | 事件後報酬 vs 隨機同窗報酬的 permutation test |
| `notebook_stage4.py` | **gate 樣板**:stationary bootstrap 的 empirical p-value + naive/stationary CI 對比 |

共用工具在 `src/quant101/resample.py`:`bootstrap_ci` / `bca_ci` / `permutation_test` /
`moving_block_indices` / `stationary_block_indices` / `stationary_bootstrap_ci`。

## Gate
能用 **stationary bootstrap** 跑出文章型態的 empirical p-value,而非只靠 closed-form 近似。

> **參考值(已用本 repo 程式驗證,合成資料)**:
> - 9 筆年報酬:percentile CI ≈ **[−5.8%, +15.2%]**、BCa ≈ **[−6.2%, +14.8%]**、
>   closed-form t-CI = **[−8.0%, +17.9%]**(與 `scipy.stats.bootstrap` 在 MC 誤差內一致)。
> - SE 膨脹:i.i.d. 時 stationary-boot SE ≈ `s/√n`;AR(1) φ=0.5 時 ≈ naive × **1.71**
>   (理論 1.73)。
> - 型態 gate:stationary-bootstrap **empirical p ≈ 0.32**,與 closed-form t p ≈ 0.46
>   並陳皆不顯著;對 overlapping 20 日報酬,naive bootstrap CI 比 stationary 版**窄約 3.9 倍**。

**正典**:Efron & Tibshirani, *An Introduction to the Bootstrap*;Politis & Romano (1994) "The Stationary Bootstrap"。
