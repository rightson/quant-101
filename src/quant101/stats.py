"""Estimation / inference primitives used across the stages.

Kept deliberately small and dependency-light (numpy + scipy + statsmodels).
Each function is written so you can read the formula off the code.
"""

from __future__ import annotations

import numpy as np
from scipy import stats

# --------------------------------------------------------------------------- #
# Binomial proportion confidence intervals (Stage 2)
# --------------------------------------------------------------------------- #

def wald_ci(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Textbook (Wald) interval p̂ ± z·sqrt(p̂(1-p̂)/n).

    Included *to show how it breaks*: for small n or p̂ near 0/1 it can poke
    outside [0, 1] and undercovers badly. Do not use it for 8/9.
    """
    z = stats.norm.ppf(1 - alpha / 2)
    p = k / n
    half = z * np.sqrt(p * (1 - p) / n)
    return p - half, p + half


def wilson_ci(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Wilson score interval — the right default for a single proportion.

    Derived by inverting the score test (solving |p̂-p|/sqrt(p(1-p)/n) = z for
    p), so it stays inside [0, 1] and keeps near-nominal coverage at small n.
    """
    z = stats.norm.ppf(1 - alpha / 2)
    p = k / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = (z / denom) * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return center - half, center + half


def agresti_coull_ci(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Agresti–Coull: "add z²/2 successes and failures, then do Wald."

    A simple, well-behaved alternative to Wilson; handy as a cross-check.
    """
    z = stats.norm.ppf(1 - alpha / 2)
    n_t = n + z**2
    p_t = (k + z**2 / 2) / n_t
    half = z * np.sqrt(p_t * (1 - p_t) / n_t)
    return p_t - half, p_t + half


def clopper_pearson_ci(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Exact (Clopper–Pearson) interval from the Beta distribution.

    Guaranteed >= nominal coverage (conservative / wider). Good "is my
    approximation sane?" anchor.
    """
    lo = 0.0 if k == 0 else stats.beta.ppf(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else stats.beta.ppf(1 - alpha / 2, k + 1, n - k)
    return lo, hi


# --------------------------------------------------------------------------- #
# Standard error of the mean (Stage 1)
# --------------------------------------------------------------------------- #

def se_mean(x: np.ndarray, ddof: int = 1) -> float:
    """SE of the sample mean = s / sqrt(n). The √n that 'n=9 eats everything'."""
    x = np.asarray(x, dtype=float)
    n = x.size
    return float(np.std(x, ddof=ddof) / np.sqrt(n))


def t_ci_mean(x: np.ndarray, alpha: float = 0.05) -> tuple[float, float]:
    """Two-sided t confidence interval for a mean (small-n appropriate)."""
    x = np.asarray(x, dtype=float)
    n = x.size
    m = x.mean()
    se = se_mean(x)
    t = stats.t.ppf(1 - alpha / 2, df=n - 1)
    return m - t * se, m + t * se


# --------------------------------------------------------------------------- #
# Power analysis (Stage 2)
# --------------------------------------------------------------------------- #

def power_one_sample_t(d: float, n: int, alpha: float = 0.05,
                       two_sided: bool = True) -> float:
    """Power of a one-sample t-test for Cohen's d at sample size n.

    Uses the non-central t distribution (ncp = d·sqrt(n)). This is what shows
    n=9 has ~0.23 power against a d≈0.46 effect.
    """
    df = n - 1
    ncp = d * np.sqrt(n)
    if two_sided:
        crit = stats.t.ppf(1 - alpha / 2, df)
        power = stats.nct.sf(crit, df, ncp) + stats.nct.cdf(-crit, df, ncp)
        if not np.isfinite(power):  # nct underflows at extreme ncp -> normal approx
            power = stats.norm.sf(crit - ncp) + stats.norm.cdf(-crit - ncp)
    else:
        crit = stats.t.ppf(1 - alpha, df)
        power = stats.nct.sf(crit, df, ncp)
        if not np.isfinite(power):
            power = stats.norm.sf(crit - ncp)
    return float(min(power, 1.0))


def n_for_power_one_sample_t(d: float, power: float = 0.8, alpha: float = 0.05,
                             two_sided: bool = True, n_max: int = 100000) -> int:
    """Smallest n whose one-sample t-test reaches the target power for d."""
    for n in range(2, n_max):
        if power_one_sample_t(d, n, alpha, two_sided) >= power:
            return n
    raise RuntimeError("target power not reached below n_max")


def power_one_sample_prop(p0: float, p1: float, n: int, alpha: float = 0.05,
                          two_sided: bool = True) -> float:
    """Normal-approx power for a one-sample proportion test (p0 vs p1)."""
    z = stats.norm.ppf(1 - alpha / (2 if two_sided else 1))
    se0 = np.sqrt(p0 * (1 - p0) / n)
    se1 = np.sqrt(p1 * (1 - p1) / n)
    crit_hi = p0 + z * se0
    crit_lo = p0 - z * se0
    upper = stats.norm.sf((crit_hi - p1) / se1)
    lower = stats.norm.cdf((crit_lo - p1) / se1) if two_sided else 0.0
    return float(upper + lower)


# --------------------------------------------------------------------------- #
# Multiple testing (Stage 3)
# --------------------------------------------------------------------------- #

def prob_any_significant(m: int, alpha: float = 0.05) -> float:
    """P(at least one false positive) across m INDEPENDENT tests = 1-(1-α)^m.

    The "family-wise error rate" if every null is true. Shows that with enough
    implicit comparisons, finding 'something significant' is essentially certain.
    """
    return float(1 - (1 - alpha) ** m)


def bonferroni(pvals, alpha: float = 0.05):
    """Bonferroni: reject p_i if p_i <= α/m. Controls FWER. Returns (reject, p_adj)."""
    p = np.asarray(pvals, dtype=float)
    m = p.size
    p_adj = np.minimum(p * m, 1.0)
    return p_adj <= alpha, p_adj


def holm(pvals, alpha: float = 0.05):
    """Holm step-down: uniformly more powerful than Bonferroni, still FWER.

    Sort ascending; threshold for the k-th smallest is α/(m-k). Returns
    (reject, p_adj) in the ORIGINAL order.
    """
    p = np.asarray(pvals, dtype=float)
    m = p.size
    order = np.argsort(p)
    p_sorted = p[order]
    p_adj_sorted = np.empty(m)
    running = 0.0
    for k in range(m):
        running = max(running, (m - k) * p_sorted[k])
        p_adj_sorted[k] = min(running, 1.0)
    p_adj = np.empty(m)
    p_adj[order] = p_adj_sorted
    return p_adj <= alpha, p_adj


def benjamini_hochberg(pvals, alpha: float = 0.05):
    """Benjamini–Hochberg: controls the false discovery rate (FDR).

    Reject the k largest-ranked p's where p_(k) <= (k/m)·α. Returns
    (reject, p_adj) in the ORIGINAL order. Less conservative than FWER methods —
    the right tool when you can tolerate a known *fraction* of false discoveries.
    """
    p = np.asarray(pvals, dtype=float)
    m = p.size
    order = np.argsort(p)
    p_sorted = p[order]
    ranks = np.arange(1, m + 1)
    # step-up adjusted p-values, enforced monotone from the top
    p_adj_sorted = np.minimum.accumulate((p_sorted * m / ranks)[::-1])[::-1]
    p_adj_sorted = np.minimum(p_adj_sorted, 1.0)
    p_adj = np.empty(m)
    p_adj[order] = p_adj_sorted
    return p_adj <= alpha, p_adj
