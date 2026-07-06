# Stage 6 精講稿 — Empirical Asset Pricing(Factor / Momentum / Mean Reversion)

主旨三句:
1. 「創新高後前瞻報酬為正」**不是 edge**,是兩個機械項相加:股市**向上 drift** +
   「創新高」所 conditioning 的 **momentum premium**。
2. 減掉這兩塊,殘差在統計上是 **0**——**沒有東西留給「主力洗盤」去解釋**。
3. 「先漲後反轉/崩」不是陰謀,是「正 drift + 肥左尾」的自然形狀:偶發 crash 只是尾巴,
   不因「剛創新高」而變兇(這條接 Stage 8)。

---

## 1. EMH 與 joint hypothesis problem(M6.1)

**Efficient Market Hypothesis**:價格已反映可得資訊,超額報酬不可持續。三種強度(weak /
semi-strong / strong)差在「資訊集」多大。

**joint hypothesis problem(Fama)**:你永遠**沒辦法單獨檢定「市場有效」**。任何「異常報酬」
的檢定,都是「**市場有效** × **你用的資產定價模型正確**」的**聯合**檢定。看到 α≠0,可能是
市場無效,也可能是你的 benchmark 模型漏了一個 factor。

**對本 case 的意義**:文章拿「創新高後報酬」對比「buy-and-hold」,隱含的 benchmark 是
「0 或無風險」。但正確的 benchmark 是**同期股市 drift + 該狀態的 factor 曝險**。用錯
benchmark,任何正報酬看起來都像「發現」——這正是 joint hypothesis problem 的實務版。

---

## 2. CAPM 與 market model(M6.2)★(Stage 7 要用)

**CAPM**:`E[r_i] − r_f = β_i·(E[r_m] − r_f)`。單一 factor(市場)決定期望超額報酬。

**Market model**(估計用的迴歸式,event study 的骨架):

```
r_i,t = α_i + β_i·r_m,t + ε_i,t
```

- `β`:市場曝險;`α`:**市場曝險解釋不了的平均報酬**——這就是 event study 要累積的
  **abnormal return**。
- **abnormal return** `AR_t = r_i,t − (α̂ + β̂·r_m,t)` = 迴歸殘差。Stage 7 把事件窗口的
  AR 累加成 CAR/BHAR。

**判讀重點**:裸報酬(raw return)把「市場整體漲」也算進「這個型態的功勞」。正確做法是先
扣掉 `α + β·r_m`,只看**超額**。`pricing.market_model` 就是這條迴歸;植入 α=0、β=1.2
的合成資產,它把 **β̂≈1.21、α̂≈0** 抓回來(R²≈0.75),證明機制正確——Stage 7 直接接。

---

## 3. Factor models 與 momentum(M6.3)

- **Fama-French 3-factor**:市場 + **SMB**(小型股)+ **HML**(價值股)。5-factor 再加
  **RMW**(獲利)、**CMA**(投資保守)。橫斷面報酬大半由這幾個 factor 解釋,不是靠選股魔法。
- **Carhart 4-factor**:3-factor + **WML(momentum,winners minus losers)**。**momentum
  是一個獨立、穩健、跨市場的 factor**(Jegadeesh-Titman 1993)。
- **關鍵**:一旦某報酬能被已知 factor 解釋,它就**不是 alpha**,是**factor 曝險的酬勞**——
  可複製、無須任何「內幕」故事。

「創新高」是什麼?**它幾乎就是 momentum 的極端版**:一支剛創 252 日新高的標的,其
trailing 12 個月報酬必然很高。所以「對創新高 conditioning」≈「對 top-momentum
conditioning」。文章的正報酬,有一塊就是 momentum premium 的機械結果。

---

## 4. 核心:把 +4.7% 拆成 drift + momentum(M6.4)

### 4.1 Time-series momentum(Moskowitz-Ooi-Pedersen 2012)

TSMOM:**過去報酬正的資產,未來報酬平均也正**。用一條迴歸捕捉:

```
r_fwd(t) = a + b·r_trailing(t) + e(t)      # b>0 就是 momentum
```

`r_trailing` 是過去 L 日報酬(動能訊號),`r_fwd` 是未來 H 日報酬。

### 4.2 分解的兩條 OLS 恆等式

令 `f`=前瞻報酬、`s`=trailing 報酬,配 `f ~ a + b·s`:

```
a + b·s̄  = f̄                        (OLS 過均值點)          = DRIFT
momentum premium = b·(s̄_cond − s̄)                          # 條件多帶的動能
model-implied conditional = drift + momentum = a + b·s̄_cond
RESIDUAL = f̄_cond − (drift + momentum)                     # drift+momentum 解釋不了的
```

`s̄_cond` 是「創新高那些日子」的平均 trailing 報酬(遠高於 `s̄`,因為它們剛創高)。
`residual` 就是**創新高那些日子的迴歸殘差平均**——扣掉 drift 與 momentum 後還剩什麼。

### 4.3 殘差的 SE 一定要用 n_eff 打折(接 Stage 5)

前瞻窗口 **overlapping**(相鄰創新高日共用大量未來天數),殘差高度自相關。若用
`s/√k` 當 SE,會把殘差的顯著性灌水。所以 `decompose_conditional_return` 用 Stage 5 的
`effective_sample_size` 把 SE 改成 `s/√n_eff`。實測:**342 個創新高窗口只值 n_eff≈45**。

### 4.4 實測結論(TAIEX 合成,創 252 日新高,H=63)

| 項 | 值 |
|---|---|
| conditional 前瞻報酬 | **+0.28%** |
| drift(無條件) | +1.52% |
| momentum premium | +0.37%(b>0, t_b≈3.4) |
| **residual** | **−1.61%**,SE=1.19%(n_eff≈45),**t≈−1.4** |
| residual 95% CI | **[−3.9%, +0.7%] — 含 0** |

**判讀**:殘差統計上**不可與 0 區分**。在這個「隨機漫步 + 正 drift」的合成序列上,前瞻報酬
其實**幾乎全是 drift**(這是隨機漫步的 Markov 性質:過去不影響未來期望,`E[f|創新高]=E[f]`)。
點估計略負只是抽樣噪音——342 個窗口只值 ~45 個獨立觀測,連 drift 本身都難精確定位
(呼應 Stage 2 的 power、Stage 5 的 n_eff)。**真實 `^TWII` 上 momentum 會是實打實的正項,
但仍是 factor 酬勞,不是洗盤。** 對照面板(見 §4.6)在植入真動能的序列上示範這點。

### 4.5 「先漲後反轉/崩」= drift + 肥左尾,不是陰謀

文章的敘事:漲上去 → 主力洗盤 → 崩。但看數字:

| 前瞻 63 日報酬 | 5% 分位 | 最差 |
|---|---|---|
| 無條件 | −12.6% | −27.0% |
| **創新高後** | −14.5% | −24.2% |

創新高後的左尾**沒有比無條件更兇**。「偶發 crash」只是同一條肥左尾的抽樣,不是「創新高」
觸發的。正 drift 的肥尾序列,本來就長成「大多時候緩漲、偶爾急殺」的樣子——不需要洗盤劇本。
(尾巴怎麼估、n=1 次危機為何估不動,留給 Stage 8。)

### 4.6 對照:當 momentum 真的存在時(植入真動能序列)

合成 TAIEX 沒有真動能(隨機漫步),所以上面 momentum≈0。用 `make_momentum_series` 造一條
**帶持續趨勢**的序列,對 top-tercile 動能 conditioning、H=63:

```
conditional = +7.62% = drift +4.77% + momentum +2.16%(b>0, t_b≈6.3) + residual +0.69%
residual t ≈ 0.1(不顯著)
```

decomposition 機器**正確把那 2.16% 歸給 momentum**,殘差仍是 0。這就是「有 signal 但早有名字」
的形狀:conditional 報酬被 drift + momentum 吃乾抹淨,**沒有任何一塊需要洗盤來解釋**。

---

## 5. long-horizon mean reversion(補充)

De Bondt-Thaler:**極長期**(3–5 年)報酬有均值回歸(過去大輸家後續反彈)。與短中期
momentum 並存、方向相反——時間尺度不同。對本 case:它提醒「先漲後反轉」在夠長的尺度上
本就存在,更不必歸因於洗盤。

---

## 6. 一頁回顧

| 概念 | 重點 | 本 case |
|---|---|---|
| joint hypothesis | 異常 = 效率 × 模型的聯合檢定 | 文章 benchmark 用錯(裸報酬 vs 0) |
| market model | `α+β·r_m`;abnormal=殘差 | 植入 β=1.2 → β̂=1.21, R²=0.75 |
| momentum factor | 創新高 ≈ top-momentum | b>0 顯著,是 factor 酬勞 |
| drift+momentum 拆解 | 殘差用 n_eff 打折 | +0.28% = 1.52% + 0.37% + (−1.61%, 不顯著) |
| 殘差 | 統計上 = 0 | CI 含 0 ⇒ 不需洗盤故事 |
| 左尾 | crash 不因創新高變兇 | q05 −14.5% vs 無條件 −12.6% |

下一站(Stage 7):把「創新高 + 急殺」重做成**正規 event study**——用本站的 market model
產 abnormal return,累成 **CAR/BHAR** 並配正確統計量,取代文章的裸報酬對照。
