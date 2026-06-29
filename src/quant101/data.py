"""Data access for the single dataset that runs through all nine stages.

The plan fixes ONE dataset — TAIEX (^TWII) daily, 1999-01 .. 2026-06 — so every
tool stacks on the same case. Real data comes from yfinance; when the network is
unavailable (e.g. a sandbox that blocks Yahoo) we fall back to a *reproducible
synthetic* series with TAIEX-like drift, volatility clustering and fat tails, so
the notebooks still run end-to-end. The synthetic path is clearly flagged.

Run `python data/build_dataset.py` once to populate data/taiex.csv + events.csv.
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
PRICE_CSV = DATA_DIR / "taiex.csv"
EVENTS_CSV = DATA_DIR / "events.csv"

START = "1999-01-01"
END = "2026-06-28"


# --------------------------------------------------------------------------- #
# Fetch / synthesize
# --------------------------------------------------------------------------- #

def fetch_real(start: str = START, end: str = END) -> pd.DataFrame:
    """Download ^TWII from Yahoo. Raises if the network/proxy blocks it."""
    import yfinance as yf

    df = yf.download(start=start, end=end, progress=False, auto_adjust=False,
                     tickers="^TWII")
    if df.empty:
        raise RuntimeError("yfinance returned no rows for ^TWII")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.rename(columns=str.lower)[["open", "high", "low", "close", "volume"]]
    df.index.name = "date"
    return df


def make_synthetic(start: str = START, end: str = END, seed: int = 19990101) -> pd.DataFrame:
    """Reproducible TAIEX-like daily OHLCV with GARCH-ish vol clustering.

    Calibrated so annualized drift ~7-8% and annualized vol ~22% (the σ that
    makes the Stage-2 power numbers line up), with occasional crash days in the
    left tail. NOT real prices — a stand-in so offline notebooks run.
    """
    rng = np.random.default_rng(seed)
    days = pd.bdate_range(start=start, end=end)
    n = len(days)

    # Target annualized vol ~22%: long-run daily var = 0.22**2/252.
    a, b = 0.08, 0.90
    long_run_var = 0.22**2 / 252
    omega = long_run_var * (1 - a - b)
    mu = 0.07 / 252 + 0.5 * long_run_var  # offset variance drag -> ~7% log drift

    sigma2 = np.empty(n)
    eps = np.empty(n)
    sigma2[0] = long_run_var
    for t in range(n):
        if t > 0:
            sigma2[t] = omega + a * eps[t - 1] ** 2 + b * sigma2[t - 1]
        # Student-t innovations -> fat tails
        z = rng.standard_t(df=5) / np.sqrt(5 / 3)
        eps[t] = np.sqrt(sigma2[t]) * z
    ret = mu + eps

    close = 6000 * np.exp(np.cumsum(ret))
    # Build plausible OHLC around the close.
    intraday = np.abs(rng.normal(0, np.sqrt(sigma2)))
    open_ = close * np.exp(-ret + rng.normal(0, 0.001, n))
    high = np.maximum(open_, close) * (1 + intraday)
    low = np.minimum(open_, close) * (1 - intraday)
    volume = (rng.lognormal(mean=21, sigma=0.4, size=n)).astype(np.int64)

    df = pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume},
        index=days,
    )
    df.index.name = "date"
    return df


# --------------------------------------------------------------------------- #
# Build / load
# --------------------------------------------------------------------------- #

def build(force: bool = False, prefer_real: bool = True) -> pd.DataFrame:
    """Create data/taiex.csv (real if possible, else synthetic) and return it."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if PRICE_CSV.exists() and not force:
        return load_prices()

    df = None
    if prefer_real:
        try:
            df = fetch_real()
            df.attrs["source"] = "yfinance:^TWII"
            print("[data] fetched real ^TWII from yfinance")
        except Exception as exc:  # network / proxy / yfinance issues
            print(f"[data] real fetch failed ({exc!s}); using synthetic fallback")
    if df is None:
        df = make_synthetic()
        df.attrs["source"] = "synthetic"
        print("[data] generated synthetic TAIEX-like series (seed=19990101)")

    df.to_csv(PRICE_CSV)
    with open(DATA_DIR / "SOURCE.txt", "w") as fh:
        fh.write(df.attrs.get("source", "unknown") + "\n")
    build_events(df).to_csv(EVENTS_CSV)
    return df


def load_prices() -> pd.DataFrame:
    if not PRICE_CSV.exists():
        return build()
    return pd.read_csv(PRICE_CSV, index_col="date", parse_dates=True)


def daily_returns(df: pd.DataFrame | None = None, kind: str = "log") -> pd.Series:
    df = load_prices() if df is None else df
    if kind == "log":
        r = np.log(df["close"]).diff()
    else:
        r = df["close"].pct_change()
    return r.dropna()


# --------------------------------------------------------------------------- #
# The event list (the object Stage 3 deconstructs)
# --------------------------------------------------------------------------- #

def build_events(df: pd.DataFrame | None = None,
                 high_window: int = 252,
                 sharp_drop_days: int = 4,
                 worst_pct: float = 0.02) -> pd.DataFrame:
    """The article's pattern: a one-year high, then within `sharp_drop_days`
    days a drop that ranks in the worst `worst_pct` of the trailing year.

    Every knob here (252? 4? 2%?) is a *researcher degree of freedom* — Stage 3
    grid-searches exactly these.
    """
    df = load_prices() if df is None else df
    close = df["close"]
    ret = close.pct_change()

    roll_max = close.rolling(high_window).max()
    is_new_high = close >= roll_max

    # trailing 1y return quantile threshold (the 2% worst day)
    thresh = ret.rolling(high_window).quantile(worst_pct)

    events = []
    idx = close.index
    for i, day in enumerate(idx):
        if not bool(is_new_high.iloc[i]):
            continue
        window = slice(i + 1, i + 1 + sharp_drop_days)
        fwd = ret.iloc[window]
        thr = thresh.iloc[window]
        hit = fwd[(fwd <= thr) & thr.notna()]
        if len(hit):
            drop_day = hit.index[0]
            events.append({
                "high_date": day,
                "drop_date": drop_day,
                "high_close": float(close.iloc[i]),
                "drop_return": float(ret.loc[drop_day]),
            })
    ev = pd.DataFrame(events)
    if len(ev):
        # collapse events whose drop windows overlap (keep first)
        ev = ev.sort_values("high_date").drop_duplicates("drop_date")
        ev = ev.set_index("high_date")
    return ev


def is_synthetic() -> bool:
    src = DATA_DIR / "SOURCE.txt"
    return (not src.exists()) or src.read_text().strip() == "synthetic"
