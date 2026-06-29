# Stage 1 習題

參考解在 `solutions/`,皆可執行。

---

## 習題 1 — 手推 Var(X̄)=σ²/n 並解釋 √n

1. 從 `Var(X̄) = Var((1/n)ΣXᵢ)` 一步步推到 `σ²/n`,標出哪一步用到「獨立」。
2. 用文字解釋 √n 的來源:為什麼是 √n 而不是 n?
3. **數值驗證**:從已知母體(取 `N(μ=0.05, σ=0.17)`,模擬年報酬)反覆抽 n 個算 X̄,
   比較 X̄ 的經驗標準差與理論 `σ/√n`,對 n ∈ {9, 100} 各驗一次。
4. **加分**:把母體換成有正自相關的 AR(1),展示經驗 SE > σ/√n(Stage 5 伏筆)。

> 對答案:`python solutions/ex1_se_derivation.py`

---

## 習題 2 — n=9 vs n=100 的 sampling distribution

對 n=9 與 n=100 各模擬 10,000 次 sample mean,畫出兩條 sampling distribution,
量出兩者 SE 的比值是否 ≈ `1/√(100/9) = 3/10 = 0.3`。

1. 模擬並印出 `SE(n=9)`, `SE(n=100)`, 與比值。
2. 確認比值 ≈ 0.3(即 n=100 的區間約是 n=9 的 1/3.33)。
3. 一句話:這就是為什麼 gate 說「n 從 9→100 區間縮成約 1/3」。

> 對答案:`python solutions/ex2_sampling_distribution.py`

---

## Notebook 任務(過 gate 前必做)

跑 `notebook_sampling.py`:用**純模擬**(非 bootstrap)展示「同一個母體、抽 9 個」會
給出多分散的 sample mean;再把文章那 9 筆事件年報酬當成「一次抽樣」,算出它的 SE,
親身感受 estimate 的不穩定。
