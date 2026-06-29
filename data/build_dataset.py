#!/usr/bin/env python3
"""Populate data/taiex.csv and data/events.csv — run this once before the notebooks.

Tries the real ^TWII series via yfinance; if the network blocks it (proxy 403,
offline sandbox, ...) it falls back to a reproducible synthetic series so the
notebooks still run. The chosen source is recorded in data/SOURCE.txt.

    python data/build_dataset.py            # real if available, else synthetic
    python data/build_dataset.py --synthetic  # force synthetic
    python data/build_dataset.py --force      # rebuild even if the csv exists
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from quant101 import data  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--synthetic", action="store_true", help="force synthetic data")
    ap.add_argument("--force", action="store_true", help="rebuild even if cached")
    args = ap.parse_args()

    df = data.build(force=args.force, prefer_real=not args.synthetic)
    ev = data.build_events(df)

    print(f"\nprices: {len(df):,} rows  {df.index.min().date()} .. {df.index.max().date()}")
    print(f"source: {(data.DATA_DIR / 'SOURCE.txt').read_text().strip()}")
    print(f"events found: {len(ev)}")
    print(f"written: {data.PRICE_CSV}")
    print(f"         {data.EVENTS_CSV}")


if __name__ == "__main__":
    main()
