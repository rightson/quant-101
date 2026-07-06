"""Event-study machinery (Stage 7).

The article's mistake this stage repairs is comparing *raw* post-event returns to
buy-and-hold. The correct object is the **abnormal return** — the return in excess
of what a normal-return model (estimated on a pre-event window) predicts — and its
significance must be judged with a statistic that survives the two things that
break naive event studies on a single clustered index:

  1. **event-induced variance** — volatility jumps around the event, so the
     estimation-window σ understates the event-window σ (Boehmer–Musumeci–Poulsen).
  2. **cross-sectional correlation** — because all events are the *same* index and
     the windows are long, clustered events (Stage 5) share calendar days, so their
     CARs overlap and are positively correlated (Kolari–Pynnönen).

Pieces:
- `run_event_study`: per-event estimation window → normal-return model (constant
  mean, or the Stage-6 market model when a benchmark is supplied) → abnormal returns
  over the event window → CAR, standardized CAR (Patell), and BHAR.
- `caar_tests`: CAAR with the plain cross-sectional t, the Patell Z, the BMP
  (standardized cross-sectional) t, and the Kolari–Pynnönen overlap-adjusted t. It
  also reports r̄ and the effective number of independent events N_eff = N/(1+(N−1)r̄)
  — the event-study face of Stage 5's effective sample size.
- `bhar_tests`: mean BHAR with the plain and the skewness-adjusted t (Johnson /
  Lyon–Barber–Tsai), the long-horizon bias of M7.4.
- `caar_bootstrap_p`: a placebo / stationary-bootstrap p-value — randomly place N
  windows of the same length and ask how often their CAAR beats the observed one.
  This reuses Stage 4's stationary bootstrap and is the dependence-honest cross-check
  the analytic KP statistic is approximating.
"""

from __future__ import annotations

import numpy as np


# --------------------------------------------------------------------------- #
# One event: estimation window → normal-return model → event-window abnormals
# --------------------------------------------------------------------------- #

def _fit_normal_model(asset_ret, market_ret, est_lo, est_hi, model, uncond_mu=None):
    """Fit the normal-return model on [est_lo, est_hi) and return a predictor.

    model='mean'       : constant-mean-return model, E[R]=μ̂ from the *pre-event*
                         window (MacKinlay's textbook default). WARNING: when events
                         are selected on past performance (new highs), this window
                         sits on the run-up, so μ̂ is biased high — the M7.4
                         benchmark-contamination trap this stage exposes.
    model='mean_uncond': constant benchmark E[R]=full-sample mean (`uncond_mu`), the
                         uncontaminated drift; σ still from the pre-event window.
    model='market'     : Stage-6 single-index model E[R]=α̂+β̂·r_m (needs a benchmark).
    Returns (predict_fn, sigma, n_params) where sigma is the estimation-window
    residual std (ddof=n_params) — the scale that standardizes the CAR.
    """
    a = asset_ret[est_lo:est_hi]
    if model == "mean":
        mu = float(np.mean(a))
        sigma = float(np.std(a, ddof=1))
        return (lambda t: mu), sigma, 1
    elif model == "mean_uncond":
        mu = float(uncond_mu)
        sigma = float(np.std(a, ddof=1))
        return (lambda t: mu), sigma, 1
    elif model == "market":
        import statsmodels.api as sm
        m = market_ret[est_lo:est_hi]
        X = sm.add_constant(m)
        res = sm.OLS(a, X).fit()
        alpha, beta = float(res.params[0]), float(res.params[1])
        sigma = float(np.std(res.resid, ddof=2))
        return (lambda t: alpha + beta * market_ret[t]), sigma, 2
    raise ValueError(f"unknown model {model!r}")


def run_event_study(asset_ret, event_positions, est_len: int = 250, gap: int = 5,
                    window=(1, 63), model: str = "mean", market_ret=None) -> dict:
    """Abnormal returns, CAR, SCAR and BHAR for every event.

    For each event position p (an integer index into `asset_ret`):
      • estimation window = [p − gap − est_len, p − gap)  (L1 days, ending `gap`
        days before the event so the event itself never contaminates the model),
      • event window      = p + range(window[0], window[1]+1),
      • AR_t = R_t − Ê[R_t];  CAR = Σ AR_t;  BHAR = Π(1+R_t) − Π(1+Ê[R_t]).

    SCAR (Patell standardization) uses the constant-mean / market-model forecast
    variance of a cumulative H-day window, σ̂²·(H + H²/L1), so estimation error is
    carried through. Events without a full estimation+event window are dropped.
    Returns arrays keyed by event plus the per-day mean abnormal path (AAR/CAAR_path).
    """
    r = np.asarray(asset_ret, dtype=float)
    if market_ret is not None:
        market_ret = np.asarray(market_ret, dtype=float)
    uncond_mu = float(np.mean(r)) if model == "mean_uncond" else None
    tau0, tau1 = window
    H = tau1 - tau0 + 1
    n = r.size

    car, scar, bhar, sigma_ev, used = [], [], [], [], []
    ar_paths = []  # AR indexed by event-time τ, for the average path & r̄
    for p in np.asarray(event_positions, dtype=int):
        est_hi = p - gap
        est_lo = est_hi - est_len
        ev_lo, ev_hi = p + tau0, p + tau1
        if est_lo < 0 or ev_hi >= n:
            continue
        predict, sigma, k = _fit_normal_model(r, market_ret, est_lo, est_hi, model,
                                              uncond_mu=uncond_mu)
        taus = np.arange(ev_lo, ev_hi + 1)
        ar = np.array([r[t] - predict(t) for t in taus])
        exp = np.array([predict(t) for t in taus])
        car_i = float(np.sum(ar))
        var_car = sigma**2 * (H + H**2 / est_len)          # Patell cumulative variance
        scar_i = car_i / np.sqrt(var_car) if var_car > 0 else np.nan
        bhar_i = float(np.prod(1 + r[taus]) - np.prod(1 + exp))
        car.append(car_i); scar.append(scar_i); bhar.append(bhar_i)
        sigma_ev.append(float(np.std(ar, ddof=1)))
        used.append(int(p)); ar_paths.append(ar)

    ar_paths = np.array(ar_paths) if ar_paths else np.empty((0, H))
    return {
        "car": np.array(car), "scar": np.array(scar), "bhar": np.array(bhar),
        "sigma_event": np.array(sigma_ev), "positions": np.array(used, dtype=int),
        "ar_paths": ar_paths, "H": H, "L1": est_len, "window": window, "model": model,
        "n_events": len(car),
        "aar": ar_paths.mean(axis=0) if len(ar_paths) else np.array([]),
        "caar_path": np.cumsum(ar_paths.mean(axis=0)) if len(ar_paths) else np.array([]),
    }


# --------------------------------------------------------------------------- #
# CAAR and its four test statistics (M7.3)
# --------------------------------------------------------------------------- #

def _overlap_rbar(positions, H: int) -> float:
    """Average pairwise CAR correlation induced by calendar-window overlap.

    Two H-day CARs on the *same* index that share k calendar days have correlation
    ≈ k/H (they are sums of the same daily returns). Averaging k/H over all event
    pairs gives the Kolari–Pynnönen r̄ specialized to a single asset — it is exactly
    the variance-inflation term: Var(CAAR) = Var_indep · [1 + (N−1)·r̄].
    """
    p = np.asarray(positions, dtype=int)
    N = p.size
    if N < 2:
        return 0.0
    tot = 0.0
    for i in range(N):
        for j in range(i + 1, N):
            overlap = max(0, H - abs(int(p[i] - p[j])))   # shared days of two H-windows
            tot += overlap / H
    return float(2 * tot / (N * (N - 1)))


def caar_tests(res: dict) -> dict:
    """CAAR with plain-t, Patell Z, BMP t, and Kolari–Pynnönen overlap-adjusted t.

    - plain  : CAAR / (s_CAR/√N)                         — assumes independent events
    - Patell : ΣSCAR / √(N·(L1−p−1)/(L1−p−3))            — uses estimation-window σ
    - BMP    : mean(SCAR) / (s_SCAR/√N)                  — robust to event-induced var
    - KP     : BMP · √((1−r̄)/(1+(N−1)·r̄))                — robust to overlap/clustering
    Also returns r̄ and N_eff = N/(1+(N−1)r̄), the effective number of independent
    events (Stage 5 in event-study clothing).
    """
    from scipy import stats as st

    car, scar = res["car"], res["scar"]
    N = car.size
    caar = float(np.mean(car))
    p_params = 1 if res["model"] == "mean" else 2
    L1 = res["L1"]

    # plain cross-sectional t
    s_car = float(np.std(car, ddof=1))
    t_plain = caar / (s_car / np.sqrt(N)) if s_car > 0 else np.nan

    # Patell Z (SCAR ~ approx N(0,1); variance correction (L1-p-1)/(L1-p-3))
    scar_var = (L1 - p_params - 1) / (L1 - p_params - 3)
    z_patell = float(np.sum(scar) / np.sqrt(N * scar_var))

    # BMP (standardized cross-sectional)
    s_scar = float(np.std(scar, ddof=1))
    t_bmp = float(np.mean(scar) / (s_scar / np.sqrt(N))) if s_scar > 0 else np.nan

    # Kolari–Pynnönen overlap correction
    rbar = _overlap_rbar(res["positions"], res["H"])
    kp_factor = np.sqrt((1 - rbar) / (1 + (N - 1) * rbar)) if rbar < 1 else 0.0
    t_kp = t_bmp * kp_factor
    n_eff = N / (1 + (N - 1) * rbar)

    def two_sided(tstat, df):
        return float(2 * st.t.sf(abs(tstat), df))

    return {
        "N": N, "CAAR": caar, "CAAR_pct": caar,
        "t_plain": float(t_plain), "p_plain": two_sided(t_plain, N - 1),
        "z_patell": z_patell, "p_patell": float(2 * st.norm.sf(abs(z_patell))),
        "t_bmp": t_bmp, "p_bmp": two_sided(t_bmp, N - 1),
        "t_kp": float(t_kp), "p_kp": two_sided(t_kp, N - 1),
        "rbar": rbar, "n_eff": float(n_eff), "kp_factor": float(kp_factor),
    }


# --------------------------------------------------------------------------- #
# BHAR and the long-horizon skewness bias (M7.4)
# --------------------------------------------------------------------------- #

def bhar_tests(res: dict) -> dict:
    """Mean BHAR with the plain t and the skewness-adjusted t (Johnson/LBT 1999).

    Long-horizon BHAR is strongly right-skewed (a few windows compound huge gains),
    so the plain t-test is mis-sized. The skewness-adjusted statistic
        t_sa = √N·(S + γ̂·S²/3 + γ̂/(6N)),  S = BHAR̄/σ_BHAR,  γ̂ = skew
    corrects the leading skewness term. Reporting both — and the skewness itself —
    is the M7.4 point: which test you use changes the verdict at long horizons.
    """
    from scipy import stats as st

    x = np.asarray(res["bhar"], dtype=float)
    N = x.size
    mean = float(np.mean(x))
    sd = float(np.std(x, ddof=1))
    skew = float(st.skew(x))
    S = mean / sd if sd > 0 else np.nan
    t_plain = S * np.sqrt(N)
    t_sa = np.sqrt(N) * (S + skew * S**2 / 3 + skew / (6 * N))
    return {
        "N": N, "BHAR_mean": mean, "BHAR_sd": sd, "skew": skew,
        "t_plain": float(t_plain), "p_plain": float(2 * st.t.sf(abs(t_plain), N - 1)),
        "t_skew_adj": float(t_sa),
    }


# --------------------------------------------------------------------------- #
# Dependence-honest cross-check: placebo / stationary-bootstrap CAAR null (Stage 4)
# --------------------------------------------------------------------------- #

def caar_bootstrap_p(asset_ret, res: dict, n_boot: int = 5000, mean_block: int = 20,
                     seed: int = 707) -> dict:
    """Empirical two-sided p-value for the observed CAAR vs randomly-placed windows.

    Draws N random start points, builds N pseudo-events with the *same* window/model,
    and forms a null CAAR. Start points come from Stage 4's stationary bootstrap so
    autocorrelation and clustering statistics are preserved. This placebo answers
    "is the observed CAAR unusual among windows placed with no regard to new-highs?"
    — the dependence-honest benchmark the analytic KP statistic approximates.
    """
    from .resample import stationary_block_indices

    r = np.asarray(asset_ret, dtype=float)
    n = r.size
    N = res["n_events"]
    tau0, tau1 = res["window"]
    H = res["H"]
    L1, gap = res["L1"], 5
    model = res["model"]
    uncond_mu = float(np.mean(r)) if model == "mean_uncond" else None
    lo_needed = L1 + gap
    hi_needed = tau1
    rng = np.random.default_rng(seed)

    obs = res["CAAR"] if "CAAR" in res else float(np.mean(res["car"]))
    null = np.empty(n_boot)
    for b in range(n_boot):
        starts = stationary_block_indices(n - lo_needed - hi_needed, mean_block, rng,
                                          size=N) + lo_needed
        cars = []
        for p in starts:
            predict, _, _ = _fit_normal_model(r, None, p - gap - L1, p - gap, model,
                                              uncond_mu=uncond_mu)
            taus = np.arange(p + tau0, p + tau1 + 1)
            cars.append(float(np.sum(r[taus] - np.array([predict(t) for t in taus]))))
        null[b] = np.mean(cars)
    p_emp = float((np.sum(np.abs(null - np.mean(null)) >= abs(obs - np.mean(null))) + 1)
                  / (n_boot + 1))
    return {"caar_obs": float(obs), "null_mean": float(np.mean(null)),
            "null_sd": float(np.std(null, ddof=1)), "p_empirical": p_emp,
            "n_boot": n_boot}
