# Stage 7 精講稿 — Event Study Methodology

主旨三句:
1. 事件研究要看的不是**裸報酬**,而是 **abnormal return**——實際報酬減掉「正常報酬模型」
   的預測。裸報酬把市場整體漂移也算進事件頭上,horizon 一換結論就翻。
2. 顯著性要用扛得住兩件事的統計量:**event-induced 變異**(Boehmer)與**事件群聚造成的
   橫斷面相關**(Kolari-Pynnönen)。單一指數的長窗口事件,群聚讓 N_eff 遠小於 N。
3. long-horizon event study 有兩個致命偏誤:**benchmark 選擇**(事件前窗口被「創新高」
   汙染)與 **skewness**(長期 BHAR 右偏,plain t 失準)。修好這兩個,文章的「坑」就消失。

---

## 1. Estimation window vs event window;abnormal return(M7.1)

事件研究的骨架是兩段不重疊的時間窗:

```
   ├──── estimation window (L1 日) ────┤   gap   ├── event window [τ1,τ2] ──┤
   估「正常報酬模型」的地方              留白避免污染   量 abnormal return 的地方
```

- **正常報酬模型**:事件**沒發生**時該有的報酬。兩種常見:
  - **constant-mean-return**:`Ê[R_t] = μ̂`(estimation window 的平均)。單一指數的誠實
    預設——它自己的漂移。
  - **market model**(Stage 6):`Ê[R_t] = α̂ + β̂·r_m,t`。需要一個 benchmark 指數。
- **abnormal return**:`AR_t = R_t − Ê[R_t]`。這是事件真正「多出來/少掉」的部分。

**為什麼一定要減 benchmark**:裸報酬 `R_t` 內含市場整體漂移。文章說「事件後裸報酬 vs
buy-and-hold 差」,等於拿「事件後報酬」去比「0 或大盤」,把大盤漲跌算成事件的功過。
`AR_t` 把正常報酬扣掉,只留事件的淨貢獻。

> **機制先驗**:對隨機事件植入已知 −5% abnormal,event study 抓回 −4.5%(t≈−4);
> 控制組(無植入)抓回 ≈0(t≈0.1)。管線先證明「有就抓得到、沒有就報 0」,再丟真事件。

---

## 2. CAR 與 BHAR(M7.2)

把單日 AR 沿 event window 累起來,兩種累法:

- **CAR**(Cumulative Abnormal Return,**相加**):`CAR = Σ_{t=τ1}^{τ2} AR_t`。線性、好做統計。
- **BHAR**(Buy-and-Hold Abnormal Return,**複利**):
  `BHAR = Π(1+R_t) − Π(1+Ê[R_t])`。對應「真的抱著」的體驗,長期偏誤更大(見 §4)。

兩者短期接近、長期分岔;文章關心的是「抱一年」,所以 BHAR 更貼近它的宣稱。

---

## 3. 正確的 test statistic(M7.3)

CAAR = 事件平均 CAR。問「CAAR ≠ 0 嗎」有四個層級的統計量,越後面越誠實:

| 統計量 | 公式(直覺) | 修的問題 |
|---|---|---|
| **plain 橫斷面 t** | `CAAR / (s_CAR/√N)` | 什麼都沒修;假設 N 個事件獨立 |
| **Patell Z** | `ΣSCAR / √(N·c)`,`SCAR=CAR/σ̂_est` | 用 estimation-window σ 標準化,但仍假設事件期變異=估計期 |
| **Boehmer (BMP)** | `mean(SCAR) / (s_SCAR/√N)` | **event-induced 變異**:事件常伴隨波動跳升,估計期 σ 低估 |
| **Kolari-Pynnönen** | `BMP · √((1−r̄)/(1+(N−1)r̄))` | **橫斷面相關**:事件群聚 ⇒ CAR 重疊相關 |

**KP 的 r̄ 與 N_eff**:同一個指數上、兩個長度 H 的 CAR,若日曆上重疊 k 天,相關約 `k/H`
(它們是同一批日報酬的和)。把 `k/H` 對所有事件對平均,就是 KP 的 `r̄`,也正是變異數放大項:

```
Var(CAAR) = Var_indep · [1 + (N−1)·r̄]      ⇒     N_eff = N / (1 + (N−1)·r̄)
```

這就是 Stage 5 的 **effective sample size** 穿上 event-study 外衣。本 case:創新高事件**群聚
在循環高點附近**(Stage 5 的結論),窗口重疊嚴重 ⇒ **26 個事件在 H=63 只值 N_eff≈16,在
H=252 只值 ≈10**。plain/BMP 假設 26 個獨立 ⇒ SE 太小 ⇒ 顯著性灌水;KP 把它打回去。

---

## 4. long-horizon 的兩個致命偏誤(M7.4)

### 4.1 benchmark 選擇 —— 本 case 最關鍵的一刀

事件是「創新高後急殺」,**每個事件都坐在漲勢的頂端**。用「事件**前** L1 日」估 constant-mean:

```
事件前 estimation window 漂移 = +24.4%/yr     ≫     全期漂移 = +7.3%/yr
```

μ̂ 被「創新高選擇」灌高 +17%/yr,對 63 日窗口 = **+4.27%**。這一塊會被記成**負的 abnormal
return**——但它是 **benchmark 汙染**,不是事件效應。這正是 Barber-Lyon 警告的「bad model /
benchmark contamination」:**當事件是用過去報酬篩出來的(創新高=高過去報酬),事件前窗口
就繼承了那個選擇。**

修法:改用**未汙染**的 benchmark(全期無條件漂移,不被單一事件的選擇帶偏)。結果:

| H | 汙染(事件前窗口) | 未汙染(全期漂移) |
|---|---|---|
| 63 | CAAR **−6.85%**(KP p=0.003) | CAAR **−2.58%**(KP p=**0.16**) |
| 252 | CAAR **−16.35%**(KP p=0.035) | CAAR **+0.72%**(KP p=**0.94**) |

換掉汙染 benchmark,H=63 的顯著性消失,H=252 連符號都翻正——**「顯著的坑」是 benchmark
造的,不是資料裡的。**

### 4.2 skewness —— 長期 BHAR 右偏

長期 BHAR 的分布嚴重**偏態**(少數窗口複利出巨大報酬),`mean/σ` 的 t 統計量會**失準**。
用 **skewness-adjusted t**(Johnson 1978 / Lyon-Barber-Tsai 1999):

```
t_sa = √N·(S + γ̂·S²/3 + γ̂/(6N)),   S = BHAR̄/σ_BHAR,  γ̂ = skewness
```

本 case H=63:平均 BHAR −7.31%、skew +0.62,plain t=−4.26 但 skewness-adj t=−3.51——修正
方向對,提醒**用哪個 t 會改變長期結論**。

### 4.3 依賴誠實的 gold-standard:stationary-bootstrap placebo

解析式(KP)在近似的東西,可以直接用 Stage 4 的 stationary bootstrap 跑出來:**隨機擺 N 個
同長度窗口**,看觀測 CAAR 在隨機擺窗分布裡多罕見。保留自相關與群聚。本 case:即使汙染版
−6.85%,bootstrap **p=0.36**;未汙染版 p=0.70 ⇒ 觀測 CAAR 落在雜訊帶內。三種依賴校正
(KP、N_eff、bootstrap)彼此印證。

---

## 5. 一頁回顧

| 概念 | 重點 | 本 case |
|---|---|---|
| abnormal return | `AR=R−Ê[R]`,別看裸報酬 | 裸報酬 horizon 一換就翻;要扣正常報酬 |
| CAR / BHAR | 相加 vs 複利 | H=63 CAAR、BHAR 都算 |
| BMP / Patell | 對 event-induced 變異穩健 | BMP t=−4.18 |
| KP / N_eff | 對群聚重疊校正 | r̄>0 ⇒ N_eff≈10–16(接 Stage 5) |
| benchmark 汙染 | 事件前窗口被創新高選擇帶偏 | +24% vs +7%/yr ⇒ 假負 4.3% |
| skewness | 長期 BHAR 右偏,plain t 失準 | skew-adj t |
| 終判 | 修好 benchmark+檢定後 | abnormal return ≈ 0,無可靠效應 |

下一站(Stage 8):事件裡真正嚇人的是**尾巴**(2007 那種崩)。但 tail probability 不能靠
一兩筆危機估——用 EVT(GEV/GPD)看「要多少獨立危機才估得動」,證明 n=9 為何遠遠不夠。
