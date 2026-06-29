#!/usr/bin/env python3
"""Stage 2 / 習題 1 參考解 — 8/9 的 Wilson vs Wald (與其他兩個比例區間).

執行:  python solutions/ex1_wilson_vs_wald.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from quant101 import stats as q  # noqa: E402

k, n = 8, 9
print(f"p̂ = {k}/{n} = {k/n:.4f}\n")

methods = {
    "Wald (錯誤示範)": q.wald_ci,
    "Wilson (正解)": q.wilson_ci,
    "Agresti-Coull": q.agresti_coull_ci,
    "Clopper-Pearson": q.clopper_pearson_ci,
}
for name, fn in methods.items():
    lo, hi = fn(k, n)
    flag = "  <-- 上界 > 1,不可能的機率!" if hi > 1 else ""
    print(f"{name:18s}: [{lo:.3f}, {hi:.3f}]{flag}")

print(
    "\n為何此處不能用 Wald:\n"
    "  (1) n=9 很小;(2) p̂=0.889 貼近 1。兩者各自就會讓 Wald 覆蓋率不足,\n"
    "  合在一起讓區間溢出 [0,1](上界 1.094)。Wilson 由 score 檢定反演而來,\n"
    "  永遠落在 [0,1],小樣本覆蓋率接近名目值,是單一比例的正確預設。\n"
    "  判讀:88% 聽來很猛,但真實命中率低到 56.5% 並未被排除 -> 形同沒有結論。"
)
