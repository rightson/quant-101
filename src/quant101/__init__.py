"""quant-101 — shared utilities for the 量化判讀力 study plan.

Everything a gate asks you to compute lives here once, so the notebooks stay
about *ideas* and the arithmetic is auditable in one place.
"""

from . import stats, data, resample  # noqa: F401

__all__ = ["stats", "data", "resample"]
