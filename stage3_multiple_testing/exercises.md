# Stage 3 習題

參考解在 `solutions/`。這一站是 ★,核心技能是「估隱性比較數 + 解釋校正後 p 膨脹」。

---

## 習題 1 — 列出文章的 researcher degrees of freedom,估隱性比較數

1. 把文章事件定義裡每一個可調參數(新高窗口、急殺天數、近期跌幅窗口、跌幅門檻、
   評估報酬 horizon)列出來,各給一組合理的候選值。
2. 算組合數 = 隱性比較數 m。
3. 算 `P(≥1 個 raw p<0.05) = 1 − (1−0.05)^m`,並算 Bonferroni 門檻 `0.05/m`。
4. 一句話:為什麼「找到一個 88% 的型態」在不知道 m 之前資訊量接近零。

> 對答案:`python solutions/ex1_degrees_of_freedom.py`
> 期望:5 個 DoF、各 4 值 ⇒ m=1024、P≈1.000、Bonferroni 門檻≈4.9e-5。

---

## 習題 2 — garden of forking paths 的實證

對一組**純噪音**(無訊號)隨機序列跑 50 個型態變體,展示總會撈到幾個「看似顯著」。

1. 生噪音序列,定義 50 個變體(改 lookback / 門檻),各做一次檢定得 p。
2. 數 raw 顯著(p<0.05)個數,對比理論期望 `m·α = 50·0.05 = 2.5`。
3. 報「最小 p 值」——它會小到看起來很厲害,但純屬運氣。
4. 套 Bonferroni / Holm / BH,確認校正後存活數 ≈ 0。
5. 重複多個 seed,確認「平均假陽性數 ≈ m·α」。

> 對答案:`python solutions/ex2_forking_paths.py`

---

## Notebook 任務(過 gate 前必做)

跑 `notebook_stage3.py`:把事件定義參數化(新高窗口、急殺天數、跌幅門檻、評估 horizon),
grid search 全部組合,展示:
- 「顯著」結果隨參數漂移(同一個資料,換個定義就翻盤);
- raw 顯著比例 ≈ α(因為合成資料無訊號);
- 做 Bonferroni / Holm / BH 校正後幾乎全滅。
