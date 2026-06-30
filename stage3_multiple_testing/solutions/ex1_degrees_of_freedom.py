#!/usr/bin/env python3
"""Stage 3 / 習題 1 參考解 — 文章的 researcher DoF 與隱性比較數.

執行:  python solutions/ex1_degrees_of_freedom.py
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from quant101 import stats as q  # noqa: E402

# 文章定義裡的 researcher degrees of freedom,各列一組合理候選值
dof = {
    "新高 lookback (交易日)":    [126, 189, 252, 378],     # 半年/9月/1年/1.5年
    "急殺判定窗口 (天)":         [2, 3, 4, 5],
    "近期跌幅窗口 (天)":         [1, 2, 3, 5],
    "跌幅門檻 (最慘百分位)":     [0.01, 0.02, 0.05, 0.10],
    "評估報酬 horizon (交易日)": [21, 63, 126, 252],        # 1/3/6/12 月
}

print("Researcher degrees of freedom:")
m = 1
for name, vals in dof.items():
    print(f"  - {name:24s}: {len(vals)} 種  {vals}")
    m *= len(vals)

alpha = 0.05
p_any = q.prob_any_significant(m, alpha)
bonf = alpha / m
print(f"\n隱性比較數 m = {' × '.join(str(len(v)) for v in dof.values())} = {m}")
print(f"P(≥1 個 raw p<{alpha}) = 1 − (1−{alpha})^{m} = {p_any:.6f}")
print(f"Bonferroni 門檻 = {alpha}/{m} = {bonf:.2e}")

# 即使非常保守(每個只取 2 值)也已經爆掉
m_cons = 2 ** len(dof)
print(f"\n保守版(每個只取 2 值):m={m_cons}, "
      f"P(≥1)={q.prob_any_significant(m_cons):.3f}")

print(
    "\n一句話:在不知道作者試了多少組(m)之前,『找到一個 88% 命中的型態』資訊量接近零——\n"
    "因為只要 m 夠大,撈到一個 p<0.05 是必然的(P≈1)。要當真,他的 p 必須小到\n"
    f"Bonferroni 門檻 {bonf:.1e} 以下,或在 out-of-sample 仍然成立。"
)
