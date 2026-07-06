# Stage 7 習題

參考解在 `solutions/`,皆可執行(需要 `statsmodels`、`scipy`)。

---

## 習題 1 — 對事件定 estimation/event window,算 CAR 與 BHAR

1. **先驗機制**:對一組**隨機**(非創新高)事件,在 event window 植入已知的 −5% abnormal
   return,用 market model 跑 event study,確認抓得回來(且控制組 ≈0)。管線先證明對,再上真事件。
2. 對「創新高+急殺」事件定 estimation window(事件前 L1=250 日,gap=5)與 event window
   [+1,+63],用 **constant-mean-return model** 算每個事件的 **CAR** 與 **BHAR**。
3. 報 **CAAR** 的四種 test statistic:plain 橫斷面 t、Patell Z、**Boehmer(BMP)**、
   **Kolari-Pynnönen**;並報 `r̄` 與 `N_eff`,說明群聚如何壓低有效事件數。
4. 對 BHAR 報 plain t 與 **skewness-adjusted t**,說明長期偏態為何讓 plain t 失準(M7.4)。

> 對答案:`python solutions/ex1_car_bhar_event_study.py`
> 期望(合成、N=26、H=63):機制驗證植入 −5.00% → 抓回 −4.47%(BMP t≈−3.98)、控制 +0.14%。
> 真事件 CAAR=−6.85%;BMP t=−4.18、**KP t=−3.25(p=0.003)**;r̄=0.024 ⇒ **N_eff≈16**。
> BHAR −7.31%(skew +0.62),plain t=−4.26、skew-adj t=−3.51。H=252 時 N_eff≈10。

---

## 習題 2 — 裸報酬 vs abnormal return,文章錯在哪

1. **重現文章的比法**:算事件後裸報酬(H=63 與 252)對比無條件均值。示範它隨 horizon
   翻來覆去(短期像落後、一年其實不落後)⇒ 裸報酬把市場漂移算進事件頭上,不是乾淨對照。
2. **揭露 benchmark 汙染**:比較「事件前 estimation window 漂移」與「全期漂移」,說明事件
   都在創新高 ⇒ μ̂ 被灌高 ⇒ constant-mean 的 abnormal return 被機械做成負的(M7.4)。
3. **修好 benchmark + 修好檢定**:換未汙染(全期漂移)benchmark 重算 CAAR,並各配 KP 與
   **stationary-bootstrap placebo**。給出終判:事件後是否有可靠的 abnormal return?

> 對答案:`python solutions/ex2_raw_vs_abnormal.py`
> 期望:事件前窗口漂移 +24.4%/yr vs 全期 +7.3%/yr ⇒ μ̂ 灌高 +4.27%/63日。
> 汙染 benchmark:CAAR −6.85%(H=63)/−16.35%(H=252);未汙染:**−2.58%(KP p=0.16)/
> +0.72%(KP p=0.94)**。bootstrap placebo:汙染版 p=0.36、未汙染版 p=0.70。
> **終判:事件後沒有可靠的 abnormal return;裸報酬對照被市場漂移+benchmark 汙染+群聚三重放大。**

---

## Notebook 任務(過 gate 前必做)

跑 `notebook_stage7.py`:
1. 機制驗證(植入 −5% AR → 抓回,控制組 ≈0)⇒ CAR/BHAR 管線可靠。
2. 真事件的 CAR + 四種 test statistic;BHAR + skewness-adjusted t。
3. benchmark 汙染對照(事件前窗口 vs 全期漂移)+ CAAR-path 圖。
4. stationary-bootstrap placebo 交叉印證。
5. 給出 gate 判斷:正規 event study 取代文章裸報酬對照,事件後 abnormal return ≈ 0。
