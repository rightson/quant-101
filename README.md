# quant-101 — 量化判讀力 study plan(可執行版)

把「從零到專精:量化判讀力」這份 study plan 落地成**可執行**的 repo。每一站的通關
gate 都是「用 TAIEX 1999–2026 資料重算某個結論」的程式產物——理論不落地成
procedural skill 就不算過。

> 完整課綱見 **[`STUDY_PLAN.md`](STUDY_PLAN.md)**。本檔是操作指南 + 進度。

## 為什麼存在
讓你能對「我發現一個市場型態」這類宣稱,在一頁內判定它是 **signal** 還是 **noise**,
並用 position sizing 而非二元進出表達不確定性。貫穿案例是一篇 finlab 文章對
TAIEX「創新高後急殺」的 9 次事件分析——九站的工具逐一拆解它。

## Quickstart
```bash
pip install -r requirements.txt
python data/build_dataset.py          # 建立 data/taiex.csv + events.csv(無網路自動用合成 fallback)

# 跑某一站的 notebook(直接執行,或先轉成 .ipynb)
python stage2_intervals_power/notebook_stage2.py
jupytext --to ipynb stage2_intervals_power/notebook_stage2.py

# 對某一站的參考解
python stage2_intervals_power/solutions/ex1_wilson_vs_wald.py
```
> 各站的 .ipynb 已隨 repo 附上(由 `notebook_*.py` 以 jupytext 轉出),可直接在 Jupyter 開。

## Repo 結構
```
quant-101/
├── STUDY_PLAN.md            # 完整九站課綱
├── requirements.txt
├── src/quant101/            # 共用工具(所有 gate 的算術集中一處,可稽核)
│   ├── stats.py             #   Wilson/Wald/AC/CP CI、SE、t-CI、power(non-central t)
│   └── data.py              #   ^TWII 載入(真實 yfinance + 合成 fallback)、事件清單
├── data/                    # build_dataset.py + 說明(產出的 csv 被 .gitignore)
├── stage0_math_foundations/ # ✅ 已交付
├── stage1_estimation/       # ✅ 已交付
├── stage2_intervals_power/  # ✅ 已交付(★ 最高 ROI 站,含完整 notebook 樣板)
└── stage3..9                # ⏳ 待交付(過一站、發下一站)
```
每站固定四個檔:`README.md`(該站總覽 + gate)、`lecture.md`(精講稿)、
`exercises.md`(習題)、`solutions/`(可執行參考解)、`notebook_*.py`(notebook 樣板)。

## 進度與已驗證的 gate

| Stage | 狀態 | Gate 重點 | 已驗證數字 |
|---|---|---|---|
| 0 數學地基 | ✅ | 從 joint 推 conditional;說清「conditioning 創新高 = conditioning 動能」 | LOTE 驗證;`E[Y\|X]≠E[Y]` 數值展示 |
| 1 Estimation | ✅ | 9 筆年報酬的 SE 與 sampling distribution | SE(n=9)≈5.6%;SE 比 √(9/100)=0.30 |
| 2 Interval/Power ★ | ✅ | 8/9 Wilson CI;n=9 power<0.3 | **Wilson [0.565, 0.980]**、Wald 上界 1.094、**power(n=9)=0.233**、**n₀.₈=39** |
| 3 Multiple Testing ★ | ⏳ | implicit comparisons 與 BH 校正 | — |
| 4 Bootstrap | ⏳ | stationary bootstrap empirical p-value | — |
| 5 Time-Series/Regime | ⏳ | Markov-switching 檢定事件群聚 | — |
| 6 Asset Pricing | ⏳ | +4.7% 拆成 drift + momentum | — |
| 7 Event Study | ⏳ | CAR/BHAR + 正確統計量 | — |
| 8 EVT/Tail | ⏳ | 估 tail 所需 crisis 觀測量 | — |
| 9 Decision/Sizing | ⏳ | signal/noise 終判 + fractional Kelly | — |

Stage 0→1→2 是不可跳的硬前置鏈,Stage 2–3 是整套 ROI 最高的兩站(見 STUDY_PLAN 依賴圖)。
本批先交付硬前置鏈到 ★ 站;其餘各站「過一站、發下一站」。

## 關於資料來源(重要)
本 sandbox 的 egress proxy 對 Yahoo 回 403,故 `build_dataset.py` 落到**可重現的合成
TAIEX-like 序列**(seed 固定)。**Stage 0–2 的 gate 不依賴真實價格**(8/9 是固定輸入、
Stage 0–1 是模擬),所以這三站的結論在合成資料下完全成立。要用真實 `^TWII`,在有網路
的機器上重跑 `python data/build_dataset.py` 即可,notebook 不需改。細節見 `data/README.md`。

## 驗證
所有參考解與 notebook 都在 commit 前實際跑過;Stage 2 的四個 gate 數字並與 statsmodels
交叉核對一致。
```bash
for f in stage*/solutions/*.py stage*/notebook_*.py; do python "$f" >/dev/null && echo "OK $f"; done
```
