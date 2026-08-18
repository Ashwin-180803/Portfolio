"""Publish gold aggregates that a warehouse or dashboard can consume."""

from __future__ import annotations

import polars as pl

from pipeline.config import GOLD_DIR, SILVER_DIR


def to_gold(silver: pl.DataFrame | None = None) -> dict[str, pl.DataFrame]:
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    trips = silver if silver is not None else pl.read_parquet(SILVER_DIR / "trips.parquet")

    daily = (
        trips.with_columns(pl.col("started_at").dt.date().alias("trip_date"))
        .group_by("trip_date")
        .agg(
            pl.len().alias("trip_count"),
            pl.col("duration_sec").mean().round(1).alias("avg_duration_sec"),
            (pl.col("member_casual").eq("member").mean() * 100).round(1).alias("member_share_pct"),
        )
        .sort("trip_date")
    )

    starts = trips.group_by("start_station_id").agg(
        pl.col("start_station_name").first().alias("station_name"),
        pl.len().alias("starts"),
    ).rename({"start_station_id": "station_id"})
    ends = trips.group_by("end_station_id").agg(
        pl.col("end_station_name").first().alias("end_name"),
        pl.len().alias("ends"),
    ).rename({"end_station_id": "station_id"})
    station_traffic = (
        starts.join(ends, on="station_id", how="full", coalesce=True)
        .with_columns(
            pl.coalesce("station_name", "end_name").alias("station_name"),
            pl.col("starts").fill_null(0),
            pl.col("ends").fill_null(0),
        )
        .select(
            "station_id",
            "station_name",
            "starts",
            "ends",
            (pl.col("starts") + pl.col("ends")).alias("total_traffic"),
        )
        .sort("total_traffic", descending=True)
    )

    membership_mix = (
        trips.group_by(["member_casual", "rideable_type"])
        .agg(
            pl.len().alias("trips"),
            pl.col("duration_sec").mean().round(1).alias("avg_duration_sec"),
        )
        .sort("trips", descending=True)
    )

    tables = {
        "daily_trips": daily,
        "station_traffic": station_traffic,
        "membership_mix": membership_mix,
    }
    for name, frame in tables.items():
        frame.write_parquet(GOLD_DIR / f"{name}.parquet")
        frame.write_csv(GOLD_DIR / f"{name}.csv")
        print(f"gold.{name}: {frame.height} rows")
    return tables
