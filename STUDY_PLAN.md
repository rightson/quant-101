# 從零到專精:量化判讀力 12–18 個月 Study Plan

> 設計目標:讓你能對「我發現一個市場型態」這類宣稱,在一頁內判定它是 **signal** 還是 **noise**,並用 position sizing 而非二元進出表達不確定性。
> 設計原則:每一站的通關 gate 都是一個「用 TAIEX 1999–2026 資料重算這篇 finlab 文章某個結論」的可執行交付物。理論不落地成 procedural skill 就不算過。

---

## 0. 全域設定

### 0.1 唯一的貫穿資料集
全程用同一份資料,讓九站的工具疊在同一個 case 上:
- **TAIEX 日線 1999-01 ~ 2026-06**(收盤、開高低、成交量)。來源:TWSE、或 `yfinance` 抓 `^TWII`。
- 對照基準:同期 buy-and-hold 報酬序列、以及一個 market-model 用的大盤報酬。
- 建議另存一份「事件清單」:文章定義的 10 次(創一年新高後 3–4 日內、近三日跌幅排進過去一年最慘前 2%)。這份清單本身就是 Stage 3 要解構的對象。

### 0.2 時間總表(realistic,非樂觀值)

| 區段 | Stage | 累積時數估計 | 月數(每週 8–10h) |
|---|---|---|---|
| 地基 | 0–1 | 60–90h | 1.5–2 |
| **核心(硬前置)** | 2–3 | 90–120h | 2.5–3 |
| 工具 | 4–5 | 90–120h | 2.5–3 |
| 金融理論 | 6–7 | 100–130h | 3–3.5 |
| 尾部與整合 | 8–9 | 110–150h | 3–4 |

Stage 1–3 一過,你對市場評論裡數字的判讀力就會 step change;那是整套投資報酬率最高的點。Stage 6–9 彼此耦合可交錯,Stage 8 (EVT) 相對獨立、卡住可暫擱。

### 0.3 每站的固定節奏(四拍)
1. **讀**(declarative):正典資源的指定章節。
2. **算**(procedural):完成該站 notebook 任務,所有量化結論自己跑出來。
3. **重做 case**:回到 finlab 文章,用本站工具重算某個結論。
4. **過 gate**:交出 gate 規定的可驗證產物。過不了就回拍 1。

### 0.4 交付節奏
一站一份,逐站深挖(全套一次傾倒會讓每站變淺)。每份含:精講稿、習題與「跑過確認可執行」的參考解、以及該站 notebook 樣板。過一站、發下一站。

---

## Stage 0 — 數學地基
**修的錯**:後面所有東西的語言;特別是 conditional vs unconditional(文章第五錯的數學根)。
**Duration**:3–4 週(已紮實可跳,但建議至少驗收 0.3)。
**Prereq**:無。

**Milestones**
- M0.1 單變數微積分:把 integration 理解成「對 density 求面積 = 求 expectation」。
- M0.2 Linear algebra:vector/matrix、投影(projection)——這是 regression 與 factor model 的骨架。
- M0.3 Probability 基礎:random variable、distribution、expectation、variance。
- M0.4 **核心**:joint / marginal / conditional distribution 三者關係;`E[Y|X]` vs `E[Y]`。

**習題**
1. 給一個二維離散 joint table,手算 marginal、conditional、`E[Y|X=x]`、`E[Y]`,並驗證 law of total expectation。
2. 用 projection 角度解釋「OLS 係數 = 把 Y 投影到 X 張成的空間」。

**Notebook 任務**:模擬一個 `X = 是否創新高`、`Y = 後續報酬` 的 joint 分布,數值上展示 `E[Y|X=創新高] ≠ E[Y]`,並說明這正是「conditioning on 創新高」在做的事。

**Gate**:能徒手從 joint density 推出 conditional density,並用一句話說清楚文章「對創新高做 conditioning,本質是對 positive momentum 做 conditioning」的數學含義。

**正典**:Blitzstein & Hwang, *Introduction to Probability*。

---

## Stage 1 — Estimation 與 Sampling Distribution
**修的錯**:錯誤 A 前半——為什麼「一個數字」背後是一個分布;`SE = σ/√n` 為何讓 n=9 吞掉一切。
**Duration**:3–4 週。**Prereq**:Stage 0。

**Milestones**
- M1.1 LLN 與 CLT:估計量為何隨 n 收斂、以什麼速率。
- M1.2 Point estimation 四性質:bias / variance / consistency / efficiency。
- M1.3 Maximum Likelihood 的直覺與計算。
- M1.4 **核心**:sampling distribution of an estimator;standard error;`SE = σ/√n`。

**習題**
1. 手推 sample mean 的 variance = σ²/n,並解釋 √n 的來源。
2. 對 n=9 與 n=100 各模擬 10,000 次,畫出 sample mean 的 sampling distribution,量出 SE 比值是否 ≈ 1/√(100/9)。

**Notebook 任務**:用 bootstrap 之外的純模擬,展示「同一個母體、抽 9 個」會給出多分散的 sample mean——把文章的 9 筆年報酬當一次抽樣,讓學習者直觀感受 estimate 的不穩定。

**Gate**:給你 9 筆年報酬,你能手算 sample mean 的 SE、說出它的 sampling distribution,並解釋 n 從 9→100 為何讓區間縮成約 1/3。

**正典**:Casella & Berger, *Statistical Inference* Ch.5–7;快版 Wasserman, *All of Statistics*。

---

## Stage 2 — Interval Estimation 與 Hypothesis Testing(含 Power)★
**修的錯**:錯誤 A 核心。Wilson CI、t 值、power 全在這。**這是整套最該先精通的一站。**
**Duration**:4–5 週。**Prereq**:Stage 1。

**Milestones**
- M2.1 Confidence interval 的「正確」詮釋(95% 指的是程序的長期覆蓋率,不是「有 95% 機率落在此區間」)。
- M2.2 Proportion 區間:為何 Wald 在小樣本/極端 p̂ 會壞掉;Wilson / Agresti-Coull / Clopper-Pearson 的差異與時機。
- M2.3 Hypothesis testing:null/alternative、Type I/II、p-value 的真正定義(與常見誤解)。
- M2.4 **核心**:statistical power 與 sample size 的關係;為何「n=9 幾乎沒有 power 拒絕任何東西」。

**習題**
1. 重算 8/9 的 Wilson CI,並與 Wald CI 對比,解釋為何此處不能用 Wald。
2. 對「1Y 中位 −1.7% vs buy-and-hold +8.5%」做一次 power analysis,求出要 power=0.8 需要多少 n。
3. 寫一段話糾正「p=0.20 代表有 80% 機率假設為真」這個常見誤讀。

**Notebook 任務**(本站有完整樣板):重算文章三個數字的 CI 與 power,並做一張「effect size × n → power」的熱力圖,標出 n=9 的位置。

**Gate**:獨立重算文章「88% = 8/9」的 Wilson CI,並用 power analysis 證明 n=9 偵測 10pp mean 差異時 power < 0.3。**(參考值:CI=[0.565,0.980]、power≈0.23、需 n≈39。)**

**正典**:Brown, Cai & DasGupta (2001) "Interval Estimation for a Binomial Proportion";power 看 Cohen, *Statistical Power Analysis*。

---

## Stage 3 — Multiple Testing 與 Research Methodology ★
**修的錯**:錯誤 B(specification mining / garden of forking paths / HARKing)。文章最致命、最常被忽略的一層。
**Duration**:4–5 週。**Prereq**:Stage 2。

**Milestones**
- M3.1 FWER vs FDR;Bonferroni / Holm / Benjamini-Hochberg。
- M3.2 Researcher degrees of freedom、p-hacking、HARKing(Hypothesizing After Results Known)。
- M3.3 Pre-registration 的科學哲學基礎;為何「先看到結果再框定義」會讓 in-sample 顯著性貶值。
- M3.4 量化直覺:每多一個自由參數,有效 p 值如何膨脹。

**習題**
1. 列出文章定義裡所有 researcher degrees of freedom(新高用一年?3–4 天?近三日?前 2%?),估計 implicit comparison 數量。
2. 對一組「都是 noise」的隨機序列跑 50 個變體,展示總會撈到幾個「看似顯著」的型態(garden of forking paths 的實證)。

**Notebook 任務**:把文章的事件定義參數化(新高窗口、急殺天數、跌幅門檻),grid search 全部組合,展示「顯著」結果隨參數漂移、且做 BH 校正後幾乎全滅。

**Gate**:對任一「回測發現」,能估計它試了多少 implicit comparison,並說明 multiple-testing 校正後 p 值如何膨脹。

**正典**:Benjamini & Hochberg (1995);Gelman & Loken (2013) "Garden of Forking Paths";Simmons, Nelson & Simonsohn (2011);Ioannidis (2005)。

---

## Stage 4 — Bootstrap 與 Resampling
**修的錯**:之後驗證的主力工具;「嚴謹版」第三點。
**Duration**:3–4 週。**Prereq**:Stage 2。

**Milestones**
- M4.1 Nonparametric bootstrap;percentile vs BCa CI。
- M4.2 Permutation test 與 Monte Carlo。
- M4.3 **核心**:block bootstrap 與 stationary bootstrap——金融報酬有 autocorrelation,naive bootstrap 會低估 SE。

**習題**
1. 對文章 9 筆年報酬跑 percentile 與 BCa bootstrap CI,對比 closed-form 結果。
2. 用 permutation test 檢定「事件後報酬」與「隨機抽的同窗報酬」是否分布不同。

**Notebook 任務**:用 stationary bootstrap 對 TAIEX 報酬重抽,跑出文章型態的 empirical p-value 與 CI,與 Stage 2 的近似值並陳。

**Gate**:能用 stationary bootstrap 跑出文章型態的 empirical p-value,而非只靠 closed-form 近似。

**正典**:Efron & Tibshirani, *An Introduction to the Bootstrap*;Politis & Romano (1994) "The Stationary Bootstrap"。

---

## Stage 5 — Time-Series Analysis 與 Regime
**修的錯**:錯誤 D(non-stationarity、non-independence、effective sample size 被壓低)。
**Duration**:5–6 週。**Prereq**:Stage 1（Stage 4 有幫助）。

**Milestones**
- M5.1 Strict vs weak stationarity、ergodicity;ACF/PACF;AR/MA/ARMA。
- M5.2 Autocorrelation 如何壓低 effective sample size。
- M5.3 Volatility clustering 與 ARCH/GARCH(為何 TAIEX 的 σ 非常數,SE 要小心)。
- M5.4 Markov-switching / structural break(形式化「跨 1999–2026 不同 regime 不能 pool」)。

**習題**
1. 對 TAIEX 報酬畫 ACF/PACF、配 GARCH(1,1),展示 conditional volatility 隨時間變。
2. 估 effective sample size,說明 9 個 cluster 在循環高點的事件其有效樣本 < 9。

**Notebook 任務**:用 Markov-switching model 把 1999–2026 切 regime,檢定 10 個事件是否 cluster 在特定 regime(即訊號是否只是「接近循環頂」的 proxy)。

**Gate**:能用 Markov-switching 切 regime 並檢定事件是否群聚,給出「此訊號是否為 regime proxy」的有依據判斷。

**正典**:Tsay, *Analysis of Financial Time Series*;進階 Hamilton, *Time Series Analysis*(含 1989 Markov-switching);Engle (1982)、Bollerslev (1986)。

---

## Stage 6 — Empirical Asset Pricing(Factor / Momentum / Mean Reversion)
**修的錯**:錯誤 E(沒認出 +4.7% 是 momentum 的機械結果);先漲後反轉為何是「drift + 偶發 crash」的自然形狀。
**Duration**:4–5 週。**Prereq**:Stage 0–2;Stage 5 有幫助。

**Milestones**
- M6.1 EMH 與 joint hypothesis problem。
- M6.2 CAPM 與 market model(Stage 7 event study 要用)。
- M6.3 Fama-French 3/5 factor、Carhart momentum。
- M6.4 Time-series momentum 與 cross-sectional momentum;long-horizon mean reversion。

**習題**
1. 把 TAIEX「創新高後 3 個月」報酬,分解成 unconditional equity drift + momentum premium 兩塊。
2. 論證殘差中是否還有任何「需要主力洗盤才能解釋」的東西。

**Notebook 任務**:對「創新高」conditioning 後的前瞻報酬,用 time-series momentum 框架重現那個正 drift,展示它不需要「洗盤」敘事。

**Gate**:能把文章 +4.7% 拆成「drift + momentum」,並說明殘差是否還需要額外故事。

**正典**:Campbell, Lo & MacKinlay, *The Econometrics of Financial Markets*;Jegadeesh & Titman (1993);Moskowitz, Ooi & Pedersen (2012);Fama & French (1993)。

---

## Stage 7 — Event Study Methodology
**修的錯**:「嚴謹版」第二點——用 abnormal return 而非裸報酬;long-horizon event study 的偏誤。
**Duration**:4 週。**Prereq**:Stage 6。

**Milestones**
- M7.1 Estimation window vs event window;abnormal return。
- M7.2 CAR(Cumulative Abnormal Return)與 BHAR(Buy-and-Hold Abnormal Return)。
- M7.3 Test statistics:Boehmer、Kolari-Pynnönen(處理 cross-sectional correlation)。
- M7.4 Long-horizon event study 的偏誤:skewness、benchmark 選擇。

**習題**
1. 對 10 次事件定 estimation/event window,算 CAR 與 BHAR 相對 market model。
2. 比較裸報酬 vs abnormal return 的結論差異,說明文章「裸報酬對 buy-and-hold」錯在哪。

**Notebook 任務**:把「創新高+急殺」重做成正規 event study,報 CAR/BHAR 與正確 test statistic。

**Gate**:能交出一份正規 event study(CAR/BHAR + 正確統計量),取代文章的裸報酬對照。

**正典**:MacKinlay (1997) "Event Studies in Economics and Finance";Campbell-Lo-MacKinlay Ch.4;Barber & Lyon (1997)、Lyon-Barber-Tsai (1999)。

---

## Stage 8 — Extreme Value Theory 與 Tail Risk
**修的錯**:錯誤 C(用 2007 一筆估 tail);「tail 論證 vs edge 論證」前半。
**Duration**:4–5 週。**Prereq**:Stage 1–2;Stage 5 有幫助。

**Milestones**
- M8.1 為何 sample mean/variance 不足以描述 tail。
- M8.2 Block maxima 與 GEV;peaks-over-threshold 與 GPD。
- M8.3 Hill estimator 估 tail index。
- M8.4 VaR / CVaR / Expected Shortfall;**核心領悟**:一個觀測值在數學上無法 identify 一個 tail probability。

**習題**
1. 對 TAIEX 報酬用 POT/GPD 估尾,畫 mean-excess plot 選門檻。
2. 推算:要可信估「此 pattern 是否抬高崩盤機率」,需多少獨立 crisis 觀測;說明 n=9 為何遠遠不夠。

**Notebook 任務**:用 GPD 配 TAIEX 左尾,展示在僅 1 筆真正 crisis(2007)下,tail probability 的估計區間有多荒謬地寬。

**Gate**:能說清楚估 tail probability 所需的獨立 crisis 觀測量,並論證 n=9 把「真正的坑在後一年」從 evidence 降級為 prior。

**正典**:McNeil, Frey & Embrechts, *Quantitative Risk Management*;入門 Coles, *An Introduction to Statistical Modeling of Extreme Values*。

---

## Stage 9 — Decision Theory、Position Sizing 與 Backtest Overfitting(整合站)
**修的錯**:錯誤 H(tail 論證該用 decision theory 表達,不該包裝成 point-estimate edge);收斂成完整 quant pipeline。
**Duration**:5–6 週。**Prereq**:Stage 2–4、6、8。

**Milestones**
- M9.1 Bayesian inference:prior/likelihood/posterior——形式化「記憶事實是 prior 不是 constraint」。
- M9.2 Statistical decision theory:loss function、expected utility;loss aversion 下「即使 mean 不顯著,左偏也可能讓先出場是對的」。
- M9.3 Kelly criterion 與 fractional Kelly 做 position sizing。
- M9.4 Backtest overfitting:Probability of Backtest Overfitting (PBO)、Deflated Sharpe Ratio;White Reality Check / Hansen SPA 串成 data-snooping 校正。

**習題**
1. 把文章的尾部論證寫成一個 decision-theoretic 問題:給定左偏分布與 loss aversion,求最適「先出場比例」。
2. 對 Stage 3 的 grid search 結果算 PBO 與 Deflated Sharpe,給出「signal or noise」終判。

**Notebook 任務**:把 Stage 2–8 的產物串成一條 pipeline——輸入一個「型態宣稱」,輸出 (a) 校正後 p 值、(b) regime proxy 檢定、(c) tail 是否可估、(d) 用 fractional Kelly 表達的 sizing 建議。

**Gate**:給你任何「我發現一個型態」的宣稱,能在一頁內判定 signal/noise,並用 position sizing 而非二元進出表達不確定性。

**正典**:Gelman et al., *Bayesian Data Analysis*;López de Prado, *Advances in Financial Machine Learning*;Bailey-Borwein-López de Prado-Zhu "Pseudo-Mathematics and Financial Charlatanism";Harvey, Liu & Zhu (2016);White (2000);Hansen (2005)。

---

## 附:依賴關係(可壓縮、不可跳號的部分)

```
Stage 0 ─► 1 ─► 2 ★ ─► 3 ★        (硬前置鏈,不可跳)
                 └─► 4 ─► 5
                 └─► 6 ─► 7
         1,2 ─────────► 8
   2,3,4,6,8 ──────────► 9          (整合站,最後)
```

★ = 整套投資報酬率最高的兩站。即使你只做到 Stage 3,對市場評論的判讀力也已 step change。
