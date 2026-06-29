# Stage 0 — 數學地基 (Math Foundations)

> **修的錯**:後面所有東西的語言;特別是 conditional vs unconditional(文章第五錯的數學根)。
> **Duration**:3–4 週(已紮實可跳,但建議至少驗收 0.3)。**Prereq**:無。

這一站不是要你變成數學家,而是要你能讀懂後面八站的語言,並且能把「對創新高做
conditioning」這句白話,翻成 `E[Y | X=創新高] ≠ E[Y]` 這個式子——這就是整篇文章
第五個錯誤的數學根。

## 四拍節奏
1. **讀**:Blitzstein & Hwang, *Introduction to Probability* — 對應章節見下。
2. **算**:跑 `notebook_conditioning.py`,把 conditioning 的效果看出來。
3. **重做 case**:把文章「創新高後報酬」當成一個 joint 分布的條件切片。
4. **過 gate**:見最下方。

## Milestones
- **M0.1** 單變數微積分:把 integration 理解成「對 density 求面積 = 求 expectation」。
- **M0.2** Linear algebra:vector / matrix、投影(projection)——regression 與 factor model 的骨架。
- **M0.3** Probability 基礎:random variable、distribution、expectation、variance。
- **M0.4 核心**:joint / marginal / conditional 三者關係;`E[Y|X]` vs `E[Y]`。

## 檔案
| 檔案 | 用途 |
|---|---|
| `lecture.md` | 精講稿(讀) |
| `exercises.md` | 習題(算) |
| `solutions/ex1_total_expectation.py` | 習題 1 參考解(可執行) |
| `solutions/ex2_ols_projection.py` | 習題 2 參考解(可執行) |
| `notebook_conditioning.py` | Notebook 樣板:模擬 `X=是否創新高`, `Y=後續報酬`,數值展示 `E[Y|X] ≠ E[Y]` |

把 `notebook_conditioning.py` 轉成 .ipynb:
```bash
jupytext --to ipynb stage0_math_foundations/notebook_conditioning.py
```
或直接執行 `python stage0_math_foundations/notebook_conditioning.py`。

## Gate
能徒手從 joint density 推出 conditional density,並用**一句話**說清楚文章
「對創新高做 conditioning,本質是對 positive momentum 做 conditioning」的數學含義。

> 參考一句話:*創新高是「近期報酬為正且大」的一個指示函數,所以
> `E[未來報酬 | 創新高]` 其實是在對「動能為正」這個事件取條件期望;它跟無條件的
> `E[未來報酬]` 不同,純粹是因為我們挑了母體裡動能為正的那一塊,不需要任何「主力」敘事。*

**正典**:Blitzstein & Hwang, *Introduction to Probability*(Ch. 7 Joint Distributions、Ch. 9 Conditional Expectation)。
