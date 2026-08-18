"""Type, clean, and dedupe bronze trips into a silver table."""

from __future__ import annotations

import polars as pl

from pipeline.config import BRONZE_DIR, SILVER_DIR

MAX_DURATION_SEC = 24 * 60 * 60


def to_silver(bronze: pl.DataFrame | None = None) -> pl.DataFrame:
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    source = bronze if bronze is not None else pl.read_parquet(BRONZE_DIR / "trips.parquet")

    silver = (
        source.with_columns(
            pl.col("ride_id").cast(pl.Utf8),
            pl.col("rideable_type").str.to_lowercase().str.strip_chars(),
            pl.col("member_casual").str.to_lowercase().str.strip_chars(),
            pl.col("started_at").str.to_datetime(strict=False),
            pl.col("ended_at").str.to_datetime(strict=False),
            pl.col("start_station_id").cast(pl.Utf8),
            pl.col("end_station_id").cast(pl.Utf8),
            pl.col("start_lat").cast(pl.Float64, strict=False),
            pl.col("start_lng").cast(pl.Float64, strict=False),
            pl.col("end_lat").cast(pl.Float64, strict=False),
            pl.col("end_lng").cast(pl.Float64, strict=False),
        )
        .with_columns(
            (pl.col("ended_at") - pl.col("started_at")).dt.total_seconds().alias("duration_sec")
        )
        .filter(
            pl.col("ride_id").is_not_null()
            & pl.col("started_at").is_not_null()
            & pl.col("ended_at").is_not_null()
            & pl.col("start_station_id").is_not_null()
            & pl.col("end_station_id").is_not_null()
            & pl.col("duration_sec").is_between(1, MAX_DURATION_SEC)
            & pl.col("member_casual").is_in(["member", "casual"])
            & pl.col("rideable_type").is_in(["classic_bike", "electric_bike"])
        )
        .unique(subset=["ride_id"], keep="first")
        .sort("started_at")
    )

    parquet = SILVER_DIR / "trips.parquet"
    csv = SILVER_DIR / "trips.csv"
    silver.write_parquet(parquet)
    silver.write_csv(csv)
    print(f"silver: {silver.height} rows (from {source.height}) → {parquet}")
    return silver
