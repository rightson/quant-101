#!/usr/bin/env python3
"""Stage 7 / 習題 1 參考解 — 對事件定 estimation/event window,算 CAR 與 BHAR.

先驗機制(植入已知 abnormal return → 抓回來),再把「創新高+急殺」10/26 次事件重做成
正規 event study:CAR、BHAR,並報四種 test statistic(plain / Patell / BMP / KP)。

執行:  python solutions/ex1_car_bhar_event_study.py
"""
import sys
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from quant101 import data, eventstudy as es, pricing as pr  # noqa: E402

data.build(prefer_real=False)
ret = data.daily_returns(kind="simple")           # Series，index=交易日
r = ret.to_numpy()
ev = data.build_events()
pos = np.array([ret.index.get_loc(d) for d in ev.index])   # 事件=急殺日在報酬序列的位置
H, L1, GAP = 63, 250, 5
print(f"[data: {'synthetic' if data.is_synthetic() else 'real ^TWII'}]  "
      f"N_events={len(pos)}  event window=[+1,+{H}]  estimation L1={L1}  gap={GAP}")

# ---------------------------------------------------------------------------- #
# 0) 機制驗證:對「隨機挑的事件」植入已知 −5% abnormal,event study 應抓回來
#    用隨機(非創新高)事件,避開 benchmark 汙染,單純測「機器會不會算」。
# ---------------------------------------------------------------------------- #
rng = np.random.default_rng(707)
rand_pos = np.sort(rng.integers(300, len(r) - 300, size=len(pos)))
INJ = -0.05
asset = pr.make_beta_asset(r, alpha_daily=0.0, beta=1.0, idio_vol=0.006, seed=707)
for p in rand_pos:
    asset[p + 1:p + H + 1] += INJ / H            # 把 −5% 均勻鋪在事件窗口
res_inj = es.run_event_study(asset, rand_pos, est_len=L1, gap=GAP, window=(1, H),
                             model="market", market_ret=r)
res_ctl = es.run_event_study(pr.make_beta_asset(r, 0.0, 1.0, 0.006, seed=707),
                             rand_pos, est_len=L1, gap=GAP, window=(1, H),
                             model="market", market_ret=r)
ci, cc = es.caar_tests(res_inj), es.caar_tests(res_ctl)
print("\n[機制驗證 — market model,隨機事件]")
print(f"  植入 CAAR={INJ:+.2%}  →  抓回 {ci['CAAR']:+.2%}  (BMP t={ci['t_bmp']:+.2f}, p={ci['p_bmp']:.4f})")
print(f"  控制組 0.00%        →  抓回 {cc['CAAR']:+.2%}  (BMP t={cc['t_bmp']:+.2f}, p={cc['p_bmp']:.3f})")
print("  => 有效應時抓得回、無效應時報 0 ⇒ 管線正確,接下來丟真事件。")

# ---------------------------------------------------------------------------- #
# 1) 真事件:constant-mean-return model(estimation window = 事件前 L1 日)
# ---------------------------------------------------------------------------- #
res = es.run_event_study(r, pos, est_len=L1, gap=GAP, window=(1, H), model="mean")
ct, bt = es.caar_tests(res), es.bhar_tests(res)
print(f"\n[創新高+急殺事件,constant-mean model,H={H}]  用得上的事件 N={res['n_events']}")
print(f"  CAAR = {ct['CAAR']:+.2%}")
print("  ── 四種 test statistic ──")
print(f"    plain 橫斷面 t   = {ct['t_plain']:+.2f}  (p={ct['p_plain']:.3f})   假設事件獨立")
print(f"    Patell Z         = {ct['z_patell']:+.2f}            用 estimation-window σ 標準化")
print(f"    BMP t            = {ct['t_bmp']:+.2f}  (p={ct['p_bmp']:.3f})   對 event-induced 變異穩健")
print(f"    Kolari-Pynnönen  = {ct['t_kp']:+.2f}  (p={ct['p_kp']:.3f})   再對群聚/重疊校正")
print(f"    r̄={ct['rbar']:.3f}  ⇒  N_eff = {ct['n_eff']:.1f}({res['n_events']} 個群聚事件只值 ~{ct['n_eff']:.0f} 個獨立)")

# ---------------------------------------------------------------------------- #
# 2) BHAR 與長期偏誤(M7.4):plain t vs skewness-adjusted t
# ---------------------------------------------------------------------------- #
print(f"\n[BHAR — buy-and-hold abnormal return,H={H}]")
print(f"  平均 BHAR = {bt['BHAR_mean']:+.2%}   skewness = {bt['skew']:+.2f}")
print(f"    plain t          = {bt['t_plain']:+.2f}  (p={bt['p_plain']:.3f})")
print(f"    skewness-adj t   = {bt['t_skew_adj']:+.2f}   (Johnson/Lyon-Barber-Tsai;偏態修正)")
print("  => 長期 BHAR 偏態使 plain t 失準;要用 skewness-adjusted(M7.4)。")

# ---------------------------------------------------------------------------- #
# 3) 一年窗口(文章的 1Y 對照)——群聚更嚴重,N_eff 掉更多
# ---------------------------------------------------------------------------- #
res1y = es.run_event_study(r, pos, est_len=L1, gap=GAP, window=(1, 252), model="mean")
c1y = es.caar_tests(res1y)
print(f"\n[1 年窗口 H=252]  CAAR={c1y['CAAR']:+.2%}  KP t={c1y['t_kp']:+.2f}(p={c1y['p_kp']:.3f})  "
      f"r̄={c1y['rbar']:.3f}  N_eff={c1y['n_eff']:.1f}")
print("  => 窗口拉到一年,重疊更嚴重,26 個事件只值 ~10 個獨立。")
print("\n注意:此 CAAR 看似顯著為負,但 benchmark 用了『事件前窗口』——事件都在創新高,")
print("      該窗口壓在漲勢上,μ̂ 被灌高 ⇒ 這負值多半是 benchmark 汙染(見 ex2)。")
