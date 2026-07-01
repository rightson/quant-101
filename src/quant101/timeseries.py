"""Time-series / regime tools (Stage 5).

Two reusable pieces the gate needs:
- `effective_sample_size`: how autocorrelation deflates the number of
  *independent* observations behind a mean (M5.2). This is the formal version of
  "9 events clustered at cyclical tops are worth fewer than 9 independent draws".
- `regime_cluster_test`: does a set of events over-concentrate in one regime,
  beyond its base rate? (binomial test, used by the Markov-switching gate).

GARCH and Markov-switching estimation themselves are done with `arch` and
`statsmodels` directly in the solutions/notebook — they are heavy models, not
one-line formulas, so wrapping them would hide more than it helps.
"""

from __future__ import annotations

import numpy as np


def effective_sample_size(x, max_lag: int | None = None) -> float:
    """Effective sample size for the mean of an autocorrelated series.

        Var(x̄) = (σ²/n)·[1 + 2·Σ_k (1 − k/n)·ρ_k]   ⟹   n_eff = n / (1 + 2·Σ …)

    The autocorrelation sum is truncated at the first non-positive ρ_k (the
    "initial positive sequence" rule; avoids adding noisy negative tail lags).
    For i.i.d. data n_eff ≈ n; for strongly positively autocorrelated data
    (e.g. overlapping H-day returns) n_eff ≈ n/H.
    """
    from statsmodels.tsa.stattools import acf

    x = np.asarray(x, dtype=float)
    n = x.size
    if max_lag is None:
        max_lag = min(n - 1, 500)
    rho = acf(x, nlags=max_lag, fft=True)[1:]
    s = 0.0
    for k, r in enumerate(rho, 1):
        if r <= 0:                      # stop at first non-positive lag
            break
        s += (1 - k / n) * r
    return float(n / (1 + 2 * s))


def regime_cluster_test(in_regime, event_idx, alternative: str = "greater"):
    """Do events over-concentrate in a regime vs its base rate?

    `in_regime`: boolean array over all days (True = day is in the regime of
    interest, e.g. the high-volatility regime).
    `event_idx`: integer indices of event days.
    Returns dict with base_rate, event_rate, k, k_in, and a binomial p-value.
    """
    in_regime = np.asarray(in_regime, dtype=bool)
    event_idx = np.asarray(event_idx, dtype=int)
    base_rate = float(in_regime.mean())
    k = event_idx.size
    k_in = int(in_regime[event_idx].sum())

    from scipy.stats import binomtest
    p = binomtest(k_in, k, base_rate, alternative=alternative).pvalue
    return {
        "base_rate": base_rate,
        "event_rate": k_in / k if k else float("nan"),
        "k": k,
        "k_in": k_in,
        "p_value": float(p),
    }


def count_regime_spells(in_regime, event_idx) -> int:
    """Number of DISTINCT regime spells that contain at least one event.

    Events packed into the same high-vol spell are not independent draws, so this
    is a crude 'effective number of independent events' — usually << len(events).
    """
    in_regime = np.asarray(in_regime, dtype=bool)
    event_idx = np.sort(np.asarray(event_idx, dtype=int))
    # label contiguous True-runs of the regime
    spell_id = np.cumsum(np.concatenate([[0], (np.diff(in_regime.astype(int)) == 1).astype(int)]))
    spells = {int(spell_id[i]) for i in event_idx if in_regime[i]}
    return len(spells)
