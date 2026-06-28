# Stage 1 — Estimation 與 Sampling Distribution

> **修的錯**:錯誤 A 前半——為什麼「一個數字」背後是一個分布;`SE = σ/√n` 為何讓 n=9 吞掉一切。
> **Duration**:3–4 週。**Prereq**:Stage 0。

文章報了一堆「單一數字」:平均 +4.7%、中位 −1.7%、88% 命中。這一站的整個重點是:
**每一個這種數字,自己都是一個會抖的隨機變數**,它的抖動幅度由 `SE = σ/√n` 決定。
當 `n=9`,`√n=3`,SE 大到幾乎任何結論都被雜訊吞掉。學會這件事,你看財經評論的數字
就會自動長出一條 error bar。

## 四拍節奏
1. **讀**:Casella & Berger Ch.5–7(快版:Wasserman *All of Statistics* Ch.6–9)。
2. **算**:跑 `notebook_sampling.py`,親眼看「抽 9 個」的 sample mean 有多散。
3. **重做 case**:把文章那 9 筆事件年報酬當「一次抽樣」,算它的 SE。
4. **過 gate**:見最下方。

## Milestones
- **M1.1** LLN 與 CLT:估計量為何隨 n 收斂、以什麼速率(√n)。
- **M1.2** Point estimation 四性質:bias / variance / consistency / efficiency。
- **M1.3** Maximum Likelihood 的直覺與計算。
- **M1.4 核心**:sampling distribution of an estimator;standard error;`SE = σ/√n`。

## 檔案
| 檔案 | 用途 |
|---|---|
| `lecture.md` | 精講稿 |
| `exercises.md` | 習題 |
| `solutions/ex1_se_derivation.py` | 手推 Var(x̄)=σ²/n + 數值驗證 |
| `solutions/ex2_sampling_distribution.py` | n=9 vs n=100 的 sampling distribution 模擬,驗證 SE 比 ≈ 1/√(100/9) |
| `notebook_sampling.py` | Notebook 樣板:純模擬展示「同母體抽 9 個」的離散程度;把文章 9 筆年報酬當一次抽樣 |

## Gate
給你 9 筆年報酬,你能:
1. 手算 sample mean 的 SE;
2. 說出它的 sampling distribution(中心 = μ,散度 = σ/√n,大 n 下近似常態);
3. 解釋 n 從 9→100 為何讓區間縮成約 **1/3**(因為 `√(100/9) = 10/3 ≈ 3.33`)。

> 參考:9 筆年報酬 `[0.085, -0.12, 0.21, -0.05, 0.30, -0.017, 0.11, -0.23, 0.16]`
> → x̄ ≈ +4.98%、s ≈ 16.84%、**SE ≈ 5.61%**;95% t-CI ≈ `[-7.97%, +17.92%]`。
> 一個「平均 +5%」其實寬到從 −8% 蓋到 +18%,跟 buy-and-hold +8.5% 完全分不開。

**正典**:Casella & Berger, *Statistical Inference* Ch.5–7;快版 Wasserman, *All of Statistics*。
