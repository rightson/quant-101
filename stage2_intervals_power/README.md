# Stage 2 — Interval Estimation 與 Hypothesis Testing(含 Power)★

> **修的錯**:錯誤 A 核心。Wilson CI、t 值、power 全在這。**這是整套最該先精通的一站。**
> **Duration**:4–5 週。**Prereq**:Stage 1。

Stage 1 教你「每個數字都有 SE」。Stage 2 教你把 SE 變成**正確的**信賴區間
(比例/小樣本不能用 Wald),並回答那個決定性的問題:**n=9 根本沒有 power 去拒絕
任何東西**——所以「沒看到顯著差異」在這裡完全不能當成「沒有差異」的證據。

這一站是 ★ 兩站之一。只做到這裡,你對市場評論數字的判讀力就已 step change。

## 四拍節奏
1. **讀**:Brown, Cai & DasGupta (2001) 比例區間;power 看 Cohen *Statistical Power Analysis*。
2. **算**:跑 `notebook_stage2.py`(本站完整樣板),重算文章三個數字的 CI 與 power。
3. **重做 case**:文章「88% = 8/9」「平均 +4.7% / 中位 −1.7% vs +8.5%」全部重算。
4. **過 gate**:見最下方。

## Milestones
- **M2.1** CI 的「正確」詮釋:95% 指**程序的長期覆蓋率**,不是「真值有 95% 機率落在此區間」。
- **M2.2** 比例區間:為何 Wald 在小樣本/極端 p̂ 會壞掉;Wilson / Agresti-Coull / Clopper-Pearson 的差異與時機。
- **M2.3** Hypothesis testing:null/alternative、Type I/II、p-value 的真正定義(與常見誤解)。
- **M2.4 核心**:statistical power 與 sample size 的關係;為何「n=9 幾乎沒有 power」。

## 檔案
| 檔案 | 用途 |
|---|---|
| `lecture.md` | 精講稿 |
| `exercises.md` | 習題 |
| `solutions/ex1_wilson_vs_wald.py` | 重算 8/9 的 Wilson vs Wald,解釋為何此處不能用 Wald |
| `solutions/ex2_power_analysis.py` | 「−1.7% vs +8.5%」power analysis;n=9 power≈0.23;求 power=0.8 的 n |
| `solutions/ex3_pvalue_misreading.md` | 糾正「p=0.20 = 80% 機率假設為真」的常見誤讀 |
| `notebook_stage2.py` | **完整樣板**:三個數字的 CI + power,並做「effect size × n → power」熱力圖,標出 n=9 |

## Gate ★
獨立重算文章「88% = 8/9」的 Wilson CI,並用 power analysis 證明 n=9 偵測 10pp mean
差異時 power < 0.3。

> **參考值(已用本 repo 程式驗證)**:
> - Wilson CI(8/9, 95%)= **[0.565, 0.980]**
> - 對照 Wald CI = [0.684, 1.094](上界 > 1,壞掉,故此處不能用 Wald)
> - power analysis(mean diff 10.2pp,annual σ=22% → Cohen's d≈0.464,one-sample t,雙尾,α=0.05):
>   **n=9 → power ≈ 0.233**;達 power=0.8 需 **n ≈ 39**。

**正典**:Brown, Cai & DasGupta (2001) "Interval Estimation for a Binomial Proportion";Cohen, *Statistical Power Analysis*。
