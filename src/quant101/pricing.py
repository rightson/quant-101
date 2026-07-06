"""Empirical asset-pricing tools (Stage 6).

The job of this stage is to show that the article's "+4.7% after a new high" is a
*mechanical* number, not evidence of an edge or of 主力洗盤 (manipulation). Two
reusable pieces do the work:

- `market_model` / `make_beta_asset`: the CAPM / single-index regression
  `r_asset = α + β·r_market + ε`. Stage 7's event study reads abnormal returns off
  exactly this, so it lives here once.
- `decompose_conditional_return`: split a *conditional* forward return
  `E[r_fwd | condition]` into (unconditional equity **drift**) + (**momentum**
  premium the condition proxies for) + (**residual**). The gate is: after removing
  drift and momentum, is the residual big enough to need an extra story? It uses a
  time-series-momentum regression (Moskowitz–Ooi–Pedersen) for the momentum term
  and Stage 5's `effective_sample_size` to keep the residual's SE honest under the
  autocorrelation that overlapping H-day returns create.

`make_momentum_series` builds a *reproducible* return series that genuinely carries
time-series momentum, so the decomposition can be seen attributing a non-zero
premium to it — the sandbox TAIEX synthetic is a random walk with drift and has
~no momentum, which is itself a teaching point (there the split is "all drift").
"""

from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS = 252


# --------------------------------------------------------------------------- #
# Forward / trailing returns (the horizons the article conditions on)
# --------------------------------------------------------------------------- #

def forward_return(prices, horizon: int) -> np.ndarray:
    """H-day-ahead simple return P_{t+H}/P_t − 1, aligned to time t (NaN at tail).

    This is "後續 N 日報酬" — and because neighbouring windows share H−1 days it is
    heavily autocorrelated, which is why the residual SE below must be deflated.
    """
    p = pd.Series(np.asarray(prices, dtype=float))
    return (p.shift(-horizon) / p - 1.0).to_numpy()


def trailing_return(prices, lookback: int) -> np.ndarray:
    """Past L-day simple return P_t/P_{t−L} − 1 at time t: the momentum signal.

    A price at a 252-day high has, by construction, a large positive trailing
    return — "creating a new high" is largely a proxy for "positive momentum".
    """
    p = pd.Series(np.asarray(prices, dtype=float))
    return (p / p.shift(lookback) - 1.0).to_numpy()


# --------------------------------------------------------------------------- #
# CAPM / single-index market model (M6.2; reused by Stage 7)
# --------------------------------------------------------------------------- #

def market_model(asset_ret, market_ret) -> dict:
    """OLS of a single index model r_asset = α + β·r_market + ε.

    α is the average return unexplained by market exposure (the "abnormal" piece an
    event study accumulates); β is the market exposure. Returns the estimates with
    t-stats plus `abnormal`, the realized residuals r_asset − (α + β·r_market).
    """
    import statsmodels.api as sm

    a = np.asarray(asset_ret, dtype=float)
    mkt = np.asarray(market_ret, dtype=float)
    mask = np.isfinite(a) & np.isfinite(mkt)
    X = sm.add_constant(mkt[mask])
    res = sm.OLS(a[mask], X).fit()
    alpha, beta = float(res.params[0]), float(res.params[1])
    abnormal = np.full(a.shape, np.nan)
    abnormal[mask] = a[mask] - (alpha + beta * mkt[mask])
    return {
        "alpha": alpha,
        "beta": beta,
        "t_alpha": float(res.tvalues[0]),
        "t_beta": float(res.tvalues[1]),
        "r2": float(res.rsquared),
        "abnormal": abnormal,
    }


# --------------------------------------------------------------------------- #
# Time-series momentum regression (M6.4; Moskowitz–Ooi–Pedersen 2012)
# --------------------------------------------------------------------------- #

def tsmom_regression(signal, fwd) -> dict:
    """OLS forward_return ~ a + b·trailing_return.

    b>0 is time-series momentum: past winners keep winning on average. The fitted
    line is the machine that turns "this day has trailing return s" into an expected
    forward return — the momentum premium the decomposition charges to a new high.
    """
    import statsmodels.api as sm

    s = np.asarray(signal, dtype=float)
    f = np.asarray(fwd, dtype=float)
    mask = np.isfinite(s) & np.isfinite(f)
    X = sm.add_constant(s[mask])
    res = sm.OLS(f[mask], X).fit()
    return {
        "a": float(res.params[0]),
        "b": float(res.params[1]),
        "t_b": float(res.tvalues[1]),
        "r2": float(res.rsquared),
        "n": int(mask.sum()),
        "signal_mean": float(np.mean(s[mask])),
    }


# --------------------------------------------------------------------------- #
# The gate: decompose a conditional forward return into drift + momentum + resid
# --------------------------------------------------------------------------- #

def decompose_conditional_return(prices, cond_mask, horizon: int,
                                 lookback: int = TRADING_DAYS) -> dict:
    """Split E[r_fwd | condition] = drift + momentum premium + residual.

    Let f = H-day forward return, s = L-day trailing return, and fit f ~ a + b·s.
    Two OLS identities do the accounting:

      • a + b·s̄ = f̄               (the line passes through the means)  = DRIFT
      • momentum premium          = b·(s̄_cond − s̄)
      • model-implied conditional = drift + momentum premium = a + b·s̄_cond
      • RESIDUAL                  = f̄_cond − (drift + momentum premium)

    The residual is the mean of the regression residuals on the conditioned days —
    what "drift + momentum" cannot explain. Its SE is deflated by the effective
    sample size (Stage 5) because forward windows overlap; without that the residual
    would look far more significant than it is. Returns every piece plus a t-stat and
    a 95% CI for the residual, so you can say whether it needs an extra story.
    """
    from scipy import stats as _stats
    from .timeseries import effective_sample_size

    prices = np.asarray(prices, dtype=float)
    cond = np.asarray(cond_mask, dtype=bool)
    f = forward_return(prices, horizon)
    s = trailing_return(prices, lookback)

    valid = np.isfinite(f) & np.isfinite(s)
    reg = tsmom_regression(s[valid], f[valid])
    a, b = reg["a"], reg["b"]

    drift = float(np.mean(f[valid]))                       # = a + b·s̄
    s_bar = float(np.mean(s[valid]))
    cmask = cond & valid
    k = int(cmask.sum())
    cond_ret = float(np.mean(f[cmask]))
    s_cond = float(np.mean(s[cmask]))
    momentum = b * (s_cond - s_bar)
    predicted = drift + momentum                            # = a + b·s_cond
    residual = cond_ret - predicted

    # residual = mean of regression residuals on conditioned days; SE via n_eff to
    # undo the overlapping-window autocorrelation.
    reg_resid = f[cmask] - (a + b * s[cmask])
    n_eff = effective_sample_size(reg_resid) if k > 3 else float(k)
    se = float(np.std(reg_resid, ddof=1) / np.sqrt(max(n_eff, 1.0)))
    t = residual / se if se > 0 else float("nan")
    z = _stats.norm.ppf(0.975)
    ci = (residual - z * se, residual + z * se)

    return {
        "horizon": horizon,
        "k": k,
        "conditional_return": cond_ret,
        "drift": drift,
        "momentum_premium": momentum,
        "residual": residual,
        "residual_se": se,
        "residual_t": float(t),
        "residual_ci": ci,
        "n_eff": float(n_eff),
        "b": b,
        "t_b": reg["t_b"],
        "trailing_mean": s_bar,
        "trailing_mean_cond": s_cond,
    }


# --------------------------------------------------------------------------- #
# Reproducible helpers for the illustrative panels
# --------------------------------------------------------------------------- #

def make_momentum_series(n: int, seed: int = 606, drift_ann: float = 0.07,
                         rho: float = 0.98, trend_vol: float = 0.0018,
                         noise_vol: float = 0.010, p0: float = 6000.0):
    """Reproducible prices whose returns carry genuine time-series momentum.

    r_t = drift + trend_t + noise_t,  trend_t = ρ·trend_{t−1} + shock. The persistent
    latent trend makes trailing returns predict forward returns (b>0), so the
    decomposition has a real momentum term to find — unlike the random-walk-with-
    drift TAIEX synthetic, where momentum ≈ 0 and a new high buys you only drift.
    Returns (prices, returns).
    """
    rng = np.random.default_rng(seed)
    mu = drift_ann / TRADING_DAYS
    trend = np.empty(n)
    trend[0] = 0.0
    shocks = rng.normal(0, trend_vol, n)
    for t in range(1, n):
        trend[t] = rho * trend[t - 1] + shocks[t]
    ret = mu + trend + rng.normal(0, noise_vol, n)
    prices = p0 * np.exp(np.cumsum(ret))
    return prices, ret


def make_beta_asset(market_ret, alpha_daily: float = 0.0, beta: float = 1.2,
                    idio_vol: float = 0.008, seed: int = 607) -> np.ndarray:
    """A reproducible asset with known α, β on the market — for the market-model demo.

    Lets the market-model regression recover the α/β you put in, so the mechanics
    Stage 7 relies on are visibly correct before real events are thrown at them.
    """
    rng = np.random.default_rng(seed)
    mkt = np.asarray(market_ret, dtype=float)
    return alpha_daily + beta * mkt + rng.normal(0, idio_vol, mkt.size)


def new_high_mask(prices, lookback: int = TRADING_DAYS) -> np.ndarray:
    """Boolean: is the close a new `lookback`-day high? The article's conditioning."""
    p = pd.Series(np.asarray(prices, dtype=float))
    roll_max = p.rolling(lookback).max()
    return (p >= roll_max).to_numpy()
