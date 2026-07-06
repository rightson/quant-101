#!/usr/bin/env python3
"""Stage 7 / 習題 2 參考解 — 裸報酬 vs abnormal return,文章錯在哪.

三件事:
  (1) 重現文章的比法:裸的事件後報酬 vs 無條件/buy-and-hold。
  (2) 揭露 benchmark 汙染:事件前 estimation window 壓在漲勢上 → μ̂ 灌高 →
      constant-mean 的 abnormal return 被機械地做成負的(M7.4 benchmark 偏誤)。
  (3) 換成未汙染 benchmark(全期漂移)+ 群聚穩健檢定(KP)+ stationary-bootstrap
      placebo,顯示 abnormal return 統計上與 0 無異。

執行:  python solutions/ex2_raw_vs_abnormal.py
"""
import sys
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from quant101 import data, eventstudy as es, pricing as pr  # noqa: E402

data.build(prefer_real=False)
ret = data.daily_returns(kind="simple")
r = ret.to_numpy()
prices = data.load_prices()["close"].to_numpy()
ev = data.build_events()
pos = np.array([ret.index.get_loc(d) for d in ev.index])
H, L1, GAP = 63, 250, 5

# ---------------------------------------------------------------------------- #
# 1) 文章的比法:裸報酬 vs 無條件(≈ buy-and-hold 的期望)
# ---------------------------------------------------------------------------- #
print("=== (1) 裸報酬對照(文章的做法)===")
for HH in (63, 252):
    f = pr.forward_return(prices, HH)
    valid = np.isfinite(f)
    postp = [f[p] for p in pos if p + HH < len(prices)]
    print(f"  H={HH:3d}: 事件後裸報酬 mean={np.mean(postp):+.2%} median={np.median(postp):+.2%}"
          f"   |   無條件 mean={np.nanmean(f[valid]):+.2%}")
print("  觀察:短期(63d)看似落後,一年(252d)其實不落後 ⇒ 『裸報酬對 buy-and-hold』隨")
print("        horizon 翻來覆去,本身就不是穩定證據——它把市場整體漂移也算進事件頭上。")

# ---------------------------------------------------------------------------- #
# 2) benchmark 汙染:事件前窗口的漂移 vs 全期漂移
# ---------------------------------------------------------------------------- #
print("\n=== (2) 為什麼 constant-mean 的 abnormal return 會騙人 ===")
full_mu = np.mean(r)
premu = [np.mean(r[p - GAP - L1:p - GAP]) for p in pos if p - GAP - L1 >= 0]
premu = float(np.mean(premu))
print(f"  全期日均漂移        = {full_mu * 252:+.1%}/yr")
print(f"  事件前 estimation 窗 = {premu * 252:+.1%}/yr   ← 事件都在創新高,窗口壓在漲勢上")
print(f"  ⇒ μ̂ 被灌高 {(premu - full_mu) * 252:+.1%}/yr,對 {H} 日窗口 = {(premu - full_mu) * H:+.2%}")
print("     這一塊會被記成『負的 abnormal return』,但它是 benchmark 汙染,不是真效應。")

# ---------------------------------------------------------------------------- #
# 3) 汙染 vs 未汙染 benchmark，各配 KP 與 bootstrap placebo
# ---------------------------------------------------------------------------- #
print("\n=== (3) 修好 benchmark + 修好檢定 ===")
for HH in (63, 252):
    print(f"\n  ── H={HH} ──")
    for model, tag in [("mean", "汙染(事件前窗口)"), ("mean_uncond", "未汙染(全期漂移)")]:
        res = es.run_event_study(r, pos, est_len=L1, gap=GAP, window=(1, HH), model=model)
        ct = es.caar_tests(res)
        bp = es.caar_bootstrap_p(r, res, n_boot=3000)
        print(f"    [{tag:16s}] CAAR={ct['CAAR']:+.2%}  "
              f"BMP t={ct['t_bmp']:+.2f}(p={ct['p_bmp']:.3f})  "
              f"KP t={ct['t_kp']:+.2f}(p={ct['p_kp']:.3f})  "
              f"bootstrap p={bp['p_empirical']:.3f}")

# ---------------------------------------------------------------------------- #
# 4) 終判
# ---------------------------------------------------------------------------- #
print("\n=== 終判 ===")
print("  • 裸報酬 vs buy-and-hold 隨 horizon 反覆,且把市場漂移算進事件頭上 ⇒ 不是乾淨對照。")
print("  • 換 abnormal return 後,若 benchmark 用事件前窗口會被『創新高選擇』汙染成假負值;")
print("    改用未汙染漂移,CAAR 收斂到接近 0。")
print("  • 即使是汙染版的負 CAAR,群聚(KP、N_eff)與 stationary-bootstrap placebo 也顯示")
print("    它落在隨機擺窗的雜訊帶內(p≫0.05)。")
print("  => 正規 event study 的結論:事件後沒有可靠的 abnormal return——文章的裸報酬對照")
print("     被『市場漂移 + benchmark 汙染 + 事件群聚』三重放大,不是真的 edge/坑。")
