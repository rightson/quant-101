# Stage 4 精講稿 — Bootstrap 與 Resampling

主旨三句:
1. **Bootstrap**:不靠公式,直接對「資料的經驗分布」重抽,讓估計量的 sampling
   distribution 自己長出來。
2. **BCa / permutation**:percentile 太天真時用 BCa 修 bias 與 skew;要檢定「兩組
   有沒有差」時用 permutation,免常態假設。
3. **核心**:金融報酬**有自相關**,naive(i.i.d.)bootstrap 把資料當可交換 →
   **低估 SE**;block / **stationary bootstrap** 重抽連續片段,保留相依,才誠實。

---

## 1. Nonparametric bootstrap:重抽經驗分布(M4.1)

手上有樣本 `x₁,…,xₙ`。Bootstrap 的想法:把**經驗分布**(每點各 1/n 機率)當成母體的
替身,從它有放回地抽 n 個,算一次統計量;重複 B 次,得到統計量的 **bootstrap 分布**。

```
for b in 1..B:
    x*  = 從 {x₁,…,xₙ} 有放回抽 n 個
    θ*_b = stat(x*)
```

`{θ*_b}` 的散度就近似 `θ̂` 的 SE;它的分位數就給出 CI。**不需要知道 θ̂ 的解析
sampling distribution**——這是 bootstrap 的賣點。

### 1.1 Percentile vs BCa

- **Percentile CI**:直接取 `{θ*_b}` 的 2.5% / 97.5% 分位。簡單,但當 `θ̂` 有偏或分布
  偏斜時,覆蓋率會歪。
- **BCa(bias-corrected & accelerated)**:用兩個修正
  - `z₀`(bias):看有多少比例的 `θ*_b` 落在 `θ̂` 以下,偏離 50% 就代表有偏。
  - `a`(acceleration):用 jackknife 估 skewness,修正「SE 隨 θ 變」。
  報酬**左偏**,所以 BCa 會把區間往下挪一點——比 percentile 準。

### 1.2 小樣本警告(本 case 的重點)

對文章的 9 筆年報酬:

| 方法 | 95% CI |
|---|---|
| percentile bootstrap | ≈ [−5.8%, +15.2%] |
| BCa bootstrap | ≈ [−6.2%, +14.8%] |
| closed-form t-CI | [−8.0%, +17.9%] |

三者都寬到從負到正十幾趴——**換工具救不了 n=9**。而且注意:**bootstrap 區間比 t-CI
還窄**。這不是 bootstrap 比較好,而是**小樣本 bootstrap 會低估寬度**(它抽不到比樣本
更極端的值,又沒有 t 分布的厚尾修正)。所以 n 很小時,closed-form t 反而較誠實;
bootstrap 不是小樣本萬靈丹。它真正的價值在**大樣本、但有結構(相依/偏斜)**的地方。

---

## 2. Permutation test 與 Monte Carlo(M4.2)

要問「A 組和 B 組的均值差,是不是只是隨機?」——**permutation test**:把兩組**混在一起**,
隨機重新貼標籤,重算差;重複很多次得到 null 分布。observed 落在 null 的哪個分位,就是
p-value。

```
observed = mean(A) − mean(B)
把 A∪B 打亂 → 前 nₐ 個當 A*、其餘當 B* → 重算差,重複 B 次
p = P(|null| ≥ |observed|)
```

好處:**不假設常態**、不需要解析分布。這是「distribution-free」的檢定。Monte Carlo 是
同一個精神的泛稱:用大量隨機模擬去逼近一個難算的機率/分布。

本 case:事件後單日報酬 vs 非事件同 offset 報酬,permutation p≈0.3(合成資料)——
「急殺後會怎樣」看不出任何有別於隨機的結構。

---

## 3. 核心:相依資料的 bootstrap(M4.3)

### 3.1 為什麼 naive bootstrap 會壞

i.i.d. bootstrap 每次獨立地抽單點,等於假設觀測**可交換(exchangeable)**。但報酬有
- **autocorrelation**(尤其 overlapping 視窗:相鄰 20 日累積報酬共用 19 天 → lag-1
  自相關 ~0.95);
- **volatility clustering**(大波動成群出現)。

把這些資料當可交換來抽,會**打散相依結構**,使 bootstrap 分布太集中 → **低估 SE、
CI 太窄**。這正是為什麼很多「回測顯著」在正確處理相依後就消失了。

### 3.2 Block bootstrap:抽連續片段

不抽單點,改抽**連續的區塊**,保留區塊內的相依:

- **Moving block bootstrap**:固定長度 `ℓ` 的區塊,隨機起點,拼到長度 n。缺點:拼接處
  仍有斷裂,且結果**不是嚴格 stationary**(端點被抽到的機率較低)。
- **Stationary bootstrap(Politis–Romano 1994)★**:區塊長度隨機,服從
  **Geometric(p = 1/mean_block)**,circular wrap-around。這樣重抽出來的序列**本身是
  stationary** 的,對起點不敏感,是相依資料的預設選擇。

`mean_block` 怎麼選:大約要 ≥ 相依的時間尺度。overlapping H 日報酬 → `mean_block ≈ H`;
一般日報酬取 n^{1/3} 量級當起點再視 ACF 調整。

### 3.3 數值上「相依 → SE 膨脹」

- i.i.d. 資料:stationary-boot 的均值 SE ≈ `s/√n`(沒有相依可保留,兩者一致)。
- AR(1) φ=0.5:stationary-boot SE ≈ naive × **1.71**(理論 `√((1+φ)/(1-φ))=1.73`)。
  對應 Stage 1 那個「effective sample size < n」的伏筆——相依讓有效樣本變少。
- 文章式的 **overlapping 20 日報酬**:stationary CI 比 naive **寬約 3.9 倍**。naive
  bootstrap 在這裡把不確定性低估到近乎誤導。

---

## 4. Gate:用 stationary bootstrap 跑型態的 empirical p-value

`notebook_stage4.py` 的流程:
1. 定義型態(創新高→急殺),取事件後單日報酬,算觀測統計量 = 事件均值 − 全樣本均值。
2. **Closed-form**:one-sample t 檢定 → p(Stage 2 風格,≈0.46)。
3. **Stationary bootstrap empirical p**:對全樣本 pool 用 stationary bootstrap 抽 k 個
   (block 保留相依)建 null,`p = P(|null| ≥ |observed|)` ≈ 0.32。
4. 兩者**並陳**:在(無動能)合成資料上都不顯著;empirical 版尊重相依,是比 closed-form
   更可信的裁決。換真實 `^TWII`(有 vol clustering)差距會更明顯。

---

## 5. 一頁回顧

| 概念 | 重點 | 本 case |
|---|---|---|
| Bootstrap | 重抽經驗分布,讓 sampling dist 自己長出來 | 9 筆 CI 仍寬到沒用 |
| Percentile vs BCa | BCa 修 bias+skew(報酬左偏) | BCa 略往下挪 |
| 小樣本警告 | bootstrap 比 t-CI 窄 = 低估 | n=9 用 t 較誠實 |
| Permutation | 打亂標籤,免常態 | 事件 vs 隨機 p≈0.3 |
| naive bootstrap 壞 | 當可交換 → 低估 SE | overlapping 報酬 naive CI 窄 3.9× |
| Stationary bootstrap | Geometric 區塊,保留相依 | empirical p≈0.32 |

下一站(Stage 5):把「相依壓低有效樣本」正式化——ACF/PACF、GARCH、以及用
Markov-switching 檢定那 9 個事件是不是只是「接近循環頂」的 regime proxy。
