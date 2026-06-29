# Stage 2 習題

參考解在 `solutions/`。這一站是 ★,務必親手把三個數字跑出來。

---

## 習題 1 — 重算 8/9 的 Wilson CI,對比 Wald

1. 算 `p̂ = 8/9` 的 Wilson CI(95%)與 Wald CI。
2. 指出 Wald 區間哪裡壞了(上界與 [0,1] 的關係),並用一句話說明**為何此處不能用 Wald**
   (n 小 + p̂ 接近 1)。
3. 加碼:也算 Agresti–Coull 與 Clopper–Pearson,確認它們都落在 [0,1] 且與 Wilson 接近。

> 對答案:`python solutions/ex1_wilson_vs_wald.py`
> 期望:Wilson=[0.565, 0.980]、Wald=[0.684, 1.094](上界>1)。

---

## 習題 2 — power analysis:「1Y 中位 −1.7% vs buy-and-hold +8.5%」

1. 把差距 10.2pp、年報酬 σ=22% 換成 Cohen's d。
2. 算 n=9 的 one-sample t-test power(雙尾,α=0.05),確認 **< 0.3**。
3. 求達 power=0.8 所需的 n。
4. 一句話:n=9「沒看到顯著差異」為什麼不能當成「沒有差異」的證據。

> 對答案:`python solutions/ex2_power_analysis.py`
> 期望:d≈0.464、power(n=9)≈0.233、n(power=0.8)≈39。

---

## 習題 3 — 糾正 p-value 誤讀

寫一段話糾正「p=0.20 代表有 80% 機率假設為真」這個常見誤讀。
要點:P(資料|H₀) ≠ P(H₀|資料);base rate / prior 的角色;Bayes 反演需要先驗。

> 參考解:`solutions/ex3_pvalue_misreading.md`

---

## Notebook 任務(過 gate 前必做)

跑 `notebook_stage2.py`(本站**完整樣板**):
- 重算文章三個數字(8/9 比例、+4.7% 平均、−1.7% vs +8.5% 差)的 CI 與 power;
- 做一張「effect size × n → power」熱力圖,標出 n=9 的位置;
- 輸出 gate 需要的全部參考值。
