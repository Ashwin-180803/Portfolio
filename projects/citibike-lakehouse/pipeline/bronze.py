"""Land raw Citi Bike CSVs as bronze Parquet without transforming values."""

from __future__ import annotations

import polars as pl

from pipeline.config import BRONZE_DIR, RAW_CSV


def land_bronze() -> pl.DataFrame:
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    frame = pl.read_csv(RAW_CSV, infer_schema_length=0)
    out = BRONZE_DIR / "trips.parquet"
    frame.write_parquet(out)
    print(f"bronze: {frame.height} rows → {out}")
    return frame
