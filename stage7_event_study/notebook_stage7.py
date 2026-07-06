# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
# ---

# %% [markdown]
# # Stage 7 Notebook — 把「創新高+急殺」重做成正規 event study(gate)
#
# 文章拿**裸報酬**對比 buy-and-hold,說「事件後表現差」。正規做法是看 **abnormal return**
# ——超出「正常報酬模型」預測的部分——並用能扛住兩件事的統計量:**event-induced 變異**
# (Boehmer)與**事件群聚造成的橫斷面相關**(Kolari-Pynnönen)。做完會看到:一旦
# benchmark 不被「創新高選擇」汙染、檢定對群聚穩健,事件後的 abnormal return 就與 0 無異。
#
# 跑法:`python notebook_stage7.py`(圖存到 figures/;需要 statsmodels)。

# %%
import sys
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from quant101 import data, eventstudy as es, pricing as pr  # noqa: E402

data.build(prefer_real=False)
ret = data.daily_returns(kind="simple")
r = ret.to_numpy()
ev = data.build_events()
pos = np.array([ret.index.get_loc(d) for d in ev.index])   # 事件 = 急殺日
H, L1, GAP = 63, 250, 5
print(f"[data: {'synthetic' if data.is_synthetic() else 'real ^TWII'}]  "
      f"N_events={len(pos)}  event window=[+1,+{H}]  L1={L1}  gap={GAP}")

# %% [markdown]
# ## 1. Estimation window vs event window;abnormal return(M7.1)
#
# 每個事件:用事件**前** L1 日估「正常報酬模型」,事件**後** [+1,+H] 是 event window;
# `AR_t = R_t − Ê[R_t]`。先驗機制:對**隨機**事件植入已知 −5% abnormal,機器應抓回來
# (隨機事件無「創新高選擇」,可乾淨測管線)。

# %%
rng = np.random.default_rng(707)
rand_pos = np.sort(rng.integers(300, len(r) - 300, size=len(pos)))
asset = pr.make_beta_asset(r, alpha_daily=0.0, beta=1.0, idio_vol=0.006, seed=707)
for p in rand_pos:
    asset[p + 1:p + H + 1] += -0.05 / H
res_inj = es.run_event_study(asset, rand_pos, est_len=L1, gap=GAP, window=(1, H),
                             model="market", market_ret=r)
res_ctl = es.run_event_study(pr.make_beta_asset(r, 0.0, 1.0, 0.006, seed=707),
                             rand_pos, est_len=L1, gap=GAP, window=(1, H),
                             model="market", market_ret=r)
ci, cc = es.caar_tests(res_inj), es.caar_tests(res_ctl)
print(f"植入 −5.00% → 抓回 {ci['CAAR']:+.2%} (BMP t={ci['t_bmp']:+.2f});"
      f"  控制 0% → {cc['CAAR']:+.2%} (t={cc['t_bmp']:+.2f})  ⇒ 管線正確")

# %% [markdown]
# ## 2. 真事件:CAR + 四種 test statistic(M7.2、M7.3)
#
# constant-mean-return model(單一指數的誠實預設:用它自己事件前的漂移當正常報酬)。

# %%
res = es.run_event_study(r, pos, est_len=L1, gap=GAP, window=(1, H), model="mean")
ct = es.caar_tests(res)
print(f"CAAR = {ct['CAAR']:+.2%}")
print(f"  plain t = {ct['t_plain']:+.2f}(p={ct['p_plain']:.3f})   假設事件獨立")
print(f"  Patell Z= {ct['z_patell']:+.2f}             estimation-window σ 標準化")
print(f"  BMP t   = {ct['t_bmp']:+.2f}(p={ct['p_bmp']:.3f})   對 event-induced 變異穩健")
print(f"  KP t    = {ct['t_kp']:+.2f}(p={ct['p_kp']:.3f})   對群聚/重疊校正")
print(f"  r̄={ct['rbar']:.3f} ⇒ N_eff={ct['n_eff']:.1f}(26 個群聚事件只值 ~{ct['n_eff']:.0f} 個獨立)")

# %% [markdown]
# ## 3. BHAR 與長期偏誤(M7.4)
#
# BHAR = 複利實際 − 複利期望。長期 BHAR 右偏,plain t 失準,要用 skewness-adjusted。

# %%
bt = es.bhar_tests(res)
print(f"平均 BHAR = {bt['BHAR_mean']:+.2%}  skew={bt['skew']:+.2f}  "
      f"plain t={bt['t_plain']:+.2f}  skew-adj t={bt['t_skew_adj']:+.2f}")

# %% [markdown]
# ## 4. benchmark 汙染:負 CAAR 是真效應還是選擇偏誤?
#
# 事件都在**創新高**,事件前 estimation window 壓在漲勢上 → μ̂ 灌高 → abnormal return
# 被機械做成負的。換**未汙染**的全期漂移當 benchmark,CAAR 應收斂到接近 0。

# %%
full_mu, premu = np.mean(r), np.mean([np.mean(r[p - GAP - L1:p - GAP]) for p in pos])
print(f"全期漂移 {full_mu*252:+.1%}/yr  vs  事件前窗口 {premu*252:+.1%}/yr  "
      f"⇒ μ̂ 灌高 {(premu-full_mu)*H:+.2%}/{H}日")
res_u = es.run_event_study(r, pos, est_len=L1, gap=GAP, window=(1, H), model="mean_uncond")
cu = es.caar_tests(res_u)
print(f"未汙染 benchmark:CAAR={cu['CAAR']:+.2%}  BMP t={cu['t_bmp']:+.2f}(p={cu['p_bmp']:.3f})  "
      f"KP t={cu['t_kp']:+.2f}(p={cu['p_kp']:.3f})")

# %% [markdown]
# ## 5. 依賴誠實的 gold-standard:stationary-bootstrap placebo(接 Stage 4)
#
# 隨機擺 N 個同長度窗口,問「觀測到的 CAAR 在隨機擺窗裡有多罕見」。保留自相關與群聚,
# 是 KP 解析式在近似的東西。

# %%
for tag, rr in [("汙染", res), ("未汙染", res_u)]:
    bp = es.caar_bootstrap_p(r, rr, n_boot=3000)
    print(f"  [{tag}] 觀測 CAAR={bp['caar_obs']:+.2%}  null_sd={bp['null_sd']:.2%}  "
          f"bootstrap p={bp['p_empirical']:.3f}")

# %% [markdown]
# ## 6. 圖:平均 abnormal-return 路徑(CAAR path),汙染 vs 未汙染
# %%
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    tau = np.arange(1, H + 1)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(tau, res["caar_path"] * 100, color="#C44E52", lw=1.8,
            label=f"汙染 benchmark (事件前窗口)  CAAR={ct['CAAR']:+.1%}")
    ax.plot(tau, res_u["caar_path"] * 100, color="#4C72B0", lw=1.8,
            label=f"未汙染 benchmark (全期漂移)  CAAR={cu['CAAR']:+.1%}")
    ax.axhline(0, color="grey", lw=0.6)
    ax.set(xlabel="event day τ (交易日,+1..+H)", ylabel="CAAR (%)",
           title=f"new-high+drop event study — CAAR path (N={res['n_events']}, "
                 f"N_eff≈{ct['n_eff']:.0f})")
    ax.legend(fontsize=8, loc="lower left")
    o = Path(__file__).resolve().parents[1] / "figures"; o.mkdir(exist_ok=True)
    fig.tight_layout(); fig.savefig(o / "stage7_caar_path.png", dpi=120)
    print(f"saved -> {o/'stage7_caar_path.png'}")
except Exception as exc:
    print(f"(figure skipped: {exc})")

# %% [markdown]
# ## 7. 過 gate 的判斷
# - **機制正確**:植入 −5% abnormal 被抓回 ≈−4.5%(t≈−4),控制組 ≈0 ⇒ CAR/BHAR 管線可靠。
# - **正規 event study**:CAR/BHAR + Boehmer/KP 統計量,取代文章的裸報酬對照。
# - **benchmark 汙染(M7.4)**:事件在創新高,事件前 estimation window 灌高 μ̂(+24% vs +7%/yr),
#   把 +4.3%/63日記成假負 abnormal;換未汙染漂移,CAAR 從 −6.85% 收到 −2.6%(H=63)、
#   −16.4% 收到 +0.7%(H=252)。
# - **群聚(接 Stage 5)**:26 個事件 r̄>0 ⇒ N_eff≈10–16;KP 與 stationary-bootstrap placebo
#   都把「顯著」打回 p≫0.05。
# - **終判**:事件後**沒有可靠的 abnormal return**;文章的裸報酬對 buy-and-hold 被
#   市場漂移 + benchmark 汙染 + 事件群聚三重放大,不是真的 edge/坑。
# - 真實 `^TWII`:`python data/build_dataset.py` 後重跑本檔即可(不需改碼)。
