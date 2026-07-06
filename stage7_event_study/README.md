# Stage 7 — Event Study Methodology

> **修的錯**:「嚴謹版」第二點——用 **abnormal return** 而非**裸報酬**;以及 long-horizon
> event study 的偏誤(benchmark 選擇、skewness)。
> **Duration**:4 週。**Prereq**:Stage 6(market model)。

文章拿「事件後裸報酬」對比「buy-and-hold」,說事件後表現差。這一站把它重做成**正規
event study**:正確的量不是裸報酬,而是 **abnormal return**——超出「正常報酬模型」預測的
部分——而且顯著性要用扛得住兩件事的統計量。做完會看到一個乾淨結論:**一旦 benchmark
不被「創新高選擇」汙染、檢定對事件群聚穩健,事件後的 abnormal return 就與 0 無異。**

## 四拍節奏
1. **讀**:MacKinlay (1997) "Event Studies in Economics and Finance";Campbell-Lo-MacKinlay Ch.4;Barber & Lyon (1997)、Lyon-Barber-Tsai (1999)。
2. **算**:跑 `notebook_stage7.py`,對事件定 estimation/event window,算 CAR/BHAR 與四種 test statistic。
3. **重做 case**:把「創新高+急殺」重做成 event study,取代文章的裸報酬對照。
4. **過 gate**:見最下方。

## Milestones
- **M7.1** Estimation window vs event window;**abnormal return** `AR_t = R_t − Ê[R_t]`(正常報酬模型:constant-mean 或 Stage 6 的 market model)。
- **M7.2** **CAR**(Cumulative Abnormal Return,加總)與 **BHAR**(Buy-and-Hold Abnormal Return,複利)。
- **M7.3** Test statistics:**Boehmer-Musumeci-Poulsen**(標準化橫斷面,對 event-induced 變異穩健)、**Kolari-Pynnönen**(再對事件群聚造成的橫斷面相關校正)。
- **M7.4** Long-horizon 偏誤:**benchmark 選擇**(事件前窗口被「創新高」汙染)、**skewness**(長期 BHAR 右偏,plain t 失準)。

## 檔案
| 檔案 | 用途 |
|---|---|
| `lecture.md` | 精講稿 |
| `exercises.md` | 習題 |
| `solutions/ex1_car_bhar_event_study.py` | 機制驗證(植入已知 AR→抓回)+ CAR/BHAR + 四種統計量 |
| `solutions/ex2_raw_vs_abnormal.py` | 裸報酬 vs abnormal;benchmark 汙染;KP + bootstrap placebo |
| `notebook_stage7.py` | **gate 樣板**:全流程 + CAAR-path 圖(汙染 vs 未汙染) |

共用工具在 `src/quant101/eventstudy.py`:`run_event_study`(estimation→AR→CAR/SCAR/BHAR)、
`caar_tests`(plain / Patell / BMP / KP,附 r̄ 與 `N_eff`)、`bhar_tests`(skewness-adjusted t)、
`caar_bootstrap_p`(stationary-bootstrap placebo,接 Stage 4)。正常報酬模型直接接 Stage 6 的
`pricing.market_model`;群聚校正的 `N_eff` 是 Stage 5 `effective_sample_size` 的 event-study 版。

## Gate
能交出一份**正規 event study**(CAR/BHAR + **正確** test statistic),取代文章的裸報酬對照。

> **參考值(已用本 repo 程式驗證,合成資料,N=26 事件,event window [+1,+H],L1=250,gap=5)**:
> - **機制驗證**(隨機事件、market model、H=63):植入 CAAR **−5.00%** → 抓回 **−4.47%**
>   (BMP t≈**−3.98**, p<0.001);控制組 0% → **+0.14%**(t≈0.10, p≈0.92)⇒ 管線正確。
> - **CAR(constant-mean model、事件前窗口、H=63)**:CAAR **−6.85%**;
>   plain t=−4.05、Patell Z=−3.60、**BMP t=−4.18(p<0.001)**、**KP t=−3.25(p=0.003)**;
>   **r̄=0.024 ⇒ N_eff≈16.2**(26 個群聚事件只值 ~16 個獨立)。
> - **BHAR(H=63)**:平均 **−7.31%**,skew=+0.62,plain t=−4.26、**skewness-adj t=−3.51**(M7.4)。
> - **benchmark 汙染(M7.4 核心)**:事件都在創新高 ⇒ 事件前 estimation window 漂移
>   **+24.4%/yr vs 全期 +7.3%/yr**,μ̂ 被灌高 **+4.27%/63日**。換**未汙染**(全期漂移)benchmark:
>   CAAR **−6.85% → −2.58%**(H=63,KP p=**0.16**,不顯著);**−16.35% → +0.72%**(H=252,KP p=**0.94**)。
> - **stationary-bootstrap placebo**(依賴誠實的 gold-standard):即使汙染版 −6.85%,
>   bootstrap **p=0.36**(H=63);未汙染版 p=0.70 ⇒ 觀測 CAAR 落在隨機擺窗的雜訊帶內。
> - **終判**:事件後**沒有可靠的 abnormal return**;文章的裸報酬對 buy-and-hold 被
>   **市場漂移 + benchmark 汙染 + 事件群聚**三重放大,不是真的 edge/坑。

**正典**:MacKinlay (1997) "Event Studies in Economics and Finance";Campbell-Lo-MacKinlay,
*The Econometrics of Financial Markets* Ch.4;Barber & Lyon (1997)、Lyon-Barber-Tsai (1999);
Boehmer, Musumeci & Poulsen (1991);Kolari & Pynnönen (2010)。
