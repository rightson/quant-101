"""Resampling tools (Stage 4): bootstrap, permutation, and block/stationary
bootstrap for serially-dependent financial returns.

Why a separate module from stats.py: these are simulation-based and share a
random-number-generator convention. Everything is seeded so notebooks reproduce.

Key idea of the station: naive (i.i.d.) bootstrap treats observations as
exchangeable. Returns are NOT — they have autocorrelation and volatility
clustering — so naive resampling destroys that dependence and *underestimates*
the standard error. Block / stationary bootstrap resample contiguous chunks to
preserve short-range dependence.
"""

from __future__ import annotations

import numpy as np

# --------------------------------------------------------------------------- #
# i.i.d. nonparametric bootstrap
# --------------------------------------------------------------------------- #

def _as_rng(seed):
    return seed if isinstance(seed, np.random.Generator) else np.random.default_rng(seed)


def bootstrap_dist(x, stat=np.mean, n_boot: int = 10000, seed=0) -> np.ndarray:
    """Bootstrap distribution of `stat`: resample x with replacement n_boot times."""
    rng = _as_rng(seed)
    x = np.asarray(x, dtype=float)
    n = x.size
    idx = rng.integers(0, n, size=(n_boot, n))
    return np.array([stat(x[i]) for i in idx])


def bootstrap_ci(x, stat=np.mean, n_boot: int = 10000, alpha: float = 0.05,
                 method: str = "percentile", seed=0):
    """Bootstrap CI. method='percentile' or 'bca'. Returns (lo, hi)."""
    if method == "bca":
        return bca_ci(x, stat, n_boot, alpha, seed)
    boot = bootstrap_dist(x, stat, n_boot, seed)
    lo, hi = np.percentile(boot, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(lo), float(hi)


def bca_ci(x, stat=np.mean, n_boot: int = 10000, alpha: float = 0.05, seed=0):
    """Bias-corrected and accelerated (BCa) interval (Efron).

    Corrects for bias (z0, via the fraction of boot stats below the observed) and
    skew (acceleration a, via jackknife). Matters here because returns are skewed,
    so a plain percentile interval is off-centre.
    """
    from scipy import stats as _ss

    x = np.asarray(x, dtype=float)
    n = x.size
    theta_hat = stat(x)
    boot = bootstrap_dist(x, stat, n_boot, seed)

    # bias correction z0
    prop = np.mean(boot < theta_hat)
    prop = min(max(prop, 1.0 / n_boot), 1 - 1.0 / n_boot)  # avoid +-inf
    z0 = _ss.norm.ppf(prop)

    # acceleration a from jackknife
    jack = np.array([stat(np.delete(x, i)) for i in range(n)])
    jack_mean = jack.mean()
    num = np.sum((jack_mean - jack) ** 3)
    den = 6.0 * (np.sum((jack_mean - jack) ** 2) ** 1.5)
    a = num / den if den != 0 else 0.0

    z = _ss.norm.ppf
    zl, zu = z(alpha / 2), z(1 - alpha / 2)
    a1 = _ss.norm.cdf(z0 + (z0 + zl) / (1 - a * (z0 + zl)))
    a2 = _ss.norm.cdf(z0 + (z0 + zu) / (1 - a * (z0 + zu)))
    lo, hi = np.percentile(boot, [100 * a1, 100 * a2])
    return float(lo), float(hi)


# --------------------------------------------------------------------------- #
# Permutation test
# --------------------------------------------------------------------------- #

def diff_in_means(a, b) -> float:
    return float(np.mean(a) - np.mean(b))


def permutation_test(a, b, stat=diff_in_means, n_perm: int = 10000,
                     alternative: str = "two-sided", seed=0):
    """Permutation test: is `stat(a, b)` larger than under random relabelling?

    Pools a and b, reshuffles the group labels n_perm times, recomputes stat.
    Returns (observed, p_value). Distribution-free; no normality assumed.
    """
    rng = _as_rng(seed)
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    observed = stat(a, b)
    pooled = np.concatenate([a, b])
    na = a.size
    null = np.empty(n_perm)
    for i in range(n_perm):
        perm = rng.permutation(pooled)
        null[i] = stat(perm[:na], perm[na:])
    if alternative == "two-sided":
        p = (np.sum(np.abs(null) >= abs(observed)) + 1) / (n_perm + 1)
    elif alternative == "greater":
        p = (np.sum(null >= observed) + 1) / (n_perm + 1)
    else:  # 'less'
        p = (np.sum(null <= observed) + 1) / (n_perm + 1)
    return float(observed), float(p)


# --------------------------------------------------------------------------- #
# Block / stationary bootstrap (the Stage-4 core)
# --------------------------------------------------------------------------- #

def moving_block_indices(n: int, block_len: int, rng, size: int | None = None) -> np.ndarray:
    """Index vector of length `size` (default n) from fixed-length blocks (circular)."""
    m = n if size is None else size
    out = np.empty(m, dtype=int)
    filled = 0
    while filled < m:
        start = rng.integers(0, n)
        take = min(block_len, m - filled)
        out[filled:filled + take] = (start + np.arange(take)) % n
        filled += take
    return out


def stationary_block_indices(n: int, mean_block: float, rng, size: int | None = None) -> np.ndarray:
    """Politis–Romano (1994) stationary bootstrap index vector of length `size`.

    Draws from a series of length n; block lengths are Geometric(p=1/mean_block),
    so the resampled series is itself stationary (unlike fixed blocks). Circular
    wrap-around. `size` defaults to n (a full replicate).
    """
    m = n if size is None else size
    p = 1.0 / mean_block
    out = np.empty(m, dtype=int)
    i = 0
    while i < m:
        start = rng.integers(0, n)
        out[i] = start
        i += 1
        while i < m and rng.random() >= p:    # extend block w.p. (1-p)
            start = (start + 1) % n
            out[i] = start
            i += 1
    return out


def block_bootstrap_dist(x, stat=np.mean, block_len: int = 20, n_boot: int = 10000,
                         seed=0, kind: str = "stationary"):
    """Bootstrap distribution of `stat` preserving short-range dependence.

    kind='stationary' (geometric blocks, mean_block=block_len) or 'moving'
    (fixed-length blocks). Use this instead of bootstrap_dist for return series.
    """
    rng = _as_rng(seed)
    x = np.asarray(x, dtype=float)
    n = x.size
    out = np.empty(n_boot)
    for b in range(n_boot):
        if kind == "moving":
            idx = moving_block_indices(n, block_len, rng)
        else:
            idx = stationary_block_indices(n, block_len, rng)
        out[b] = stat(x[idx])
    return out


def stationary_bootstrap_ci(x, stat=np.mean, mean_block: float = 20,
                            n_boot: int = 10000, alpha: float = 0.05, seed=0):
    """Percentile CI from the stationary bootstrap (dependence-aware)."""
    boot = block_bootstrap_dist(x, stat, mean_block, n_boot, seed, kind="stationary")
    lo, hi = np.percentile(boot, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(lo), float(hi)
