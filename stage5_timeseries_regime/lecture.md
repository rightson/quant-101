# Stage 5 精講稿 — Time-Series Analysis 與 Regime

主旨三句:
1. 報酬**不是 i.i.d.**:它有 autocorrelation、volatility clustering、以及跨期的
   **regime** 變化。前面各站的公式默認可交換/獨立,這裡把那個假設拆掉。
2. 自相關**壓低 effective sample size**:overlapping 報酬的有效樣本約只有 n/H。
3. 那 9~10 個事件多半**擠在同一種 regime**(循環頂/高波動),所以「訊號」很可能只是
   「身處某 regime」的 proxy——這就是錯誤 D 的核心。

---

## 1. Stationarity、ergodicity、ACF/PACF、ARMA(M5.1)

- **Strict stationarity**:整個聯合分布不隨時間平移而變。**Weak(covariance)
  stationarity**:均值、變異數固定,自相關只依賴 lag。金融報酬約略 weak stationary,
  但**波動**與**regime**會破壞它。
- **Ergodicity**:時間平均 → 母體平均。若資料跨越不能 pool 的 regime,ergodicity 可疑,
  「用整段歷史估一個數」就危險。
- **ACF/PACF**:自相關函數 `ρ_k = Corr(x_t, x_{t-k})`;PACF 是扣掉中間 lag 後的直接相關。
  用來判斷 AR/MA 階數。
- **AR/MA/ARMA**:`AR(p)` 用過去值、`MA(q)` 用過去衝擊、`ARMA` 兩者兼有,描述線性相依。

**判讀重點**:報酬的 ACF 幾乎為 0(≈0.01)——報酬本身近似白噪音、不可線性預測。
但這**不代表獨立**:見下一節的波動。

---

## 2. Autocorrelation 壓低 effective sample size(M5.2)★

對相依資料,均值的變異數不是 `σ²/n`:

```
Var(x̄) = (σ²/n)·[1 + 2·Σ_{k≥1}(1 − k/n)ρ_k]
n_eff  = n / [1 + 2·Σ …]
```

- i.i.d.:括號 ≈ 1 → `n_eff ≈ n`。
- 正自相關:括號 > 1 → **`n_eff < n`**,SE 被低估。

**最狠的例子:overlapping 報酬。** 文章講「後續 N 日報酬」,相鄰視窗共用 N−1 天,
人為造出 lag-1 自相關 ~0.95。實測:

| 序列 | n | n_eff | n/n_eff |
|---|---|---|---|
| 日報酬 | 7170 | 6851 | 1.0 |
| overlapping 5d | 7166 | 1239 | ≈ 5 |
| overlapping 20d | 7151 | 350 | ≈ 20 |
| overlapping 60d | 7111 | 130 | ≈ 60 |

**`n/n_eff ≈ H`**:用 overlapping H 日報酬時,你以為有幾千個獨立觀測,其實只有約 n/H。
把 n 當自由度算的 t 值、SE、顯著性,全部灌水。這是「回測看起來很顯著」的常見暗坑。

同理,那 9~10 個事件若擠在少數幾個時間叢集,**有效獨立事件數 < 事件數**——Stage 2 已經
很慘的 power,還要再打折。

---

## 3. Volatility clustering 與 ARCH/GARCH(M5.3)

報酬的 ACF≈0,但 **報酬² 的 ACF 明顯 > 0**(實測 lag-1≈0.13):大波動跟著大波動、
小波動跟著小波動——**volatility clustering**。σ 不是常數,是**動態**的。

**GARCH(1,1)**:

```
σ²_t = ω + α·ε²_{t-1} + β·σ²_{t-1}
```

- `α`:上期衝擊的即時效應;`β`:波動的記憶。
- **persistence = α+β**,越接近 1 波動衝擊衰退越慢。實測 α≈0.07、β≈0.90、
  **α+β≈0.97**;conditional volatility 年化在 ~12%–51% 間擺盪(≈4 倍差)。

**判讀重點**:用「全期單一 σ」算的 SE/CI/VaR 會錯,因為此刻的 σ 可能是平時的好幾倍。
危機期的報酬不能跟平靜期的報酬混在一起當同分布抽樣。(Stage 8 的尾部估計接這條。)

---

## 4. 核心:Regime 與「不能 pool」(M5.4)

**Markov-switching model**(Hamilton 1989):假設有若干個隱藏狀態(regime),各有自己的
均值/變異數,狀態間依一個 Markov 轉移矩陣切換。配 2-regime、允許 switching variance,
模型會自己找出**高波動**與**低波動**兩個狀態,並給每天屬於各 regime 的 smoothed 機率。

實測(合成資料):

- 低波動 σ²≈0.64、高波動 σ²≈2.69(高波動 σ 約 2.1 倍);高波動 regime 佔全期 ~27%。
- 轉移持續:`P[留在低]≈0.955`、`P[留在高]≈0.900`——接近 1,代表這是**真的 regime**
  (會賴著不走),不是隨機亂跳。

**Structural break**:另一種形式化「參數在某時點永久改變」的工具(Chow、Bai-Perron)。
與 Markov-switching 互補:一個是反覆切換的狀態,一個是一次性的斷點。共同訊息:
**跨 1999–2026 不同 regime,把資料 pool 成一個母體來估一個數,是有問題的。**

### 4.1 訊號是不是 regime proxy(gate 的問法)

把型態事件標在 regime 上,檢定它們是否**過度集中**在某個 regime:

- 事件落在高波動 regime 的比例 = **82%(18/22)**,而基準率只有 **27%**。
- binomial test `p ≈ 1.7e-7`:**顯著群聚**。

結論:「創新高後急殺」幾乎等於「市場正處於高波動 regime」。這個「訊號」**大半是 regime
的 proxy**,不是獨立 edge。你以為抓到一個型態,其實只是抓到「現在很亂」。
(合成資料只有 GARCH 造成的波動 regime;真實 `^TWII` 還疊加牛熊循環,proxy 效果更強。)

---

## 5. 一頁回顧

| 概念 | 重點 | 本 case |
|---|---|---|
| 報酬 ACF≈0 | 近似白噪音,但不獨立 | lag-1≈0.01 |
| 波動叢聚 | 報酬² 有自相關 | lag-1≈0.13 |
| GARCH | σ 動態、persistence≈1 | α+β≈0.97,σ 擺 4× |
| effective sample | overlapping ⇒ n_eff≈n/H | 20d:7151→350 |
| Markov-switching | 高/低波動 regime,轉移持續 | 高波動佔 27%,P[stay]≈0.9 |
| regime proxy | 事件過度集中在高波動 | 82% vs 27%,p≈1.7e-7 |

下一站(Stage 6):把「創新高後 +4.7%」拆成 **市場 drift + momentum premium**——
用資產定價的語言說明那個正報酬是機械結果,不需要「主力洗盤」。
