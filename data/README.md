# data/ — 唯一貫穿資料集

全程用同一份資料,讓九站的工具疊在同一個 case 上。

- **目標**:TAIEX 日線 1999-01 ~ 2026-06(open/high/low/close/volume)。
- **來源**:TWSE,或 `yfinance` 抓 `^TWII`。
- **對照**:同期 buy-and-hold 報酬序列、market-model 用的大盤報酬(後續站)。
- **事件清單**:文章型態(創一年新高後 3–4 日內、跌幅排進過去一年最慘前 2%)——
  這份清單本身就是 Stage 3 要解構的對象。

## 產生資料

```bash
python data/build_dataset.py            # 有網路 -> 抓真實 ^TWII;否則合成 fallback
python data/build_dataset.py --synthetic  # 強制合成
python data/build_dataset.py --force      # 重建
```

產出(都被 .gitignore,可隨時重建):
- `data/taiex.csv` — OHLCV
- `data/events.csv` — 事件清單(欄位:high_date, drop_date, high_close, drop_return)
- `data/SOURCE.txt` — `yfinance:^TWII` 或 `synthetic`

## 關於合成 fallback

當網路被擋(如本 sandbox 的 proxy 對 Yahoo 回 403),`build_dataset.py` 會生一份
**可重現**(seed=19990101)的 TAIEX-like 序列:約 7% 年漂移、~18–22% 年化波動、
GARCH(1,1) 波動叢聚、Student-t 厚尾(偶發崩盤)。**它不是真實價格**,只是讓離線
notebook 能跑完。

重點:
- **Stage 0–2 的 gate 不依賴真實價格**——「8/9」是固定輸入,Stage 0–1 是模擬。
  所以這三站在合成資料下結論完全有效。
- **合成序列沒有內建動能**(報酬近似 martingale)。所以在合成資料上,「創新高後報酬」
  的條件差會接近 0 或為負;換成真實 `^TWII` 後,因市場真有動能,通常翻正。
  這反而是 Stage 0 的好教材:sign 取決於資料裡有沒有相關,不取決於敘事。
- 想用真實資料:在有網路的機器上跑 `python data/build_dataset.py`,其餘 notebook 不變。
