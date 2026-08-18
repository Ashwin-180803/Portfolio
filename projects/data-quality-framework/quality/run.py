from __future__ import annotations

from datetime import datetime
from pathlib import Path

from quality.checks import (
    SuiteResult,
    check_accepted_values,
    check_freshness,
    check_null_rates,
    check_referential,
    check_row_count,
    check_schema,
    load_csv,
)
from quality.config import FIXTURES
from quality.contracts import load_contract
from quality.report import write_reports


def _table_path(name: str, data_root: Path | None) -> Path:
    mapping = {
        "silver_trips": ("silver/trips.csv", "silver_trips.csv"),
        "gold_daily_trips": ("gold/daily_trips.csv", "gold_daily_trips.csv"),
        "gold_station_traffic": ("gold/station_traffic.csv", "gold_station_traffic.csv"),
    }
    rel, fixture = mapping[name]
    if data_root:
        candidate = data_root / rel
        if candidate.exists():
            return candidate
    return FIXTURES / fixture


def run(data_root: Path | None = None, as_of: datetime | None = None) -> SuiteResult:
    silver_contract = load_contract("silver_trips")
    gold_contract = load_contract("gold_daily_trips")
    silver = load_csv(_table_path("silver_trips", data_root))
    daily = load_csv(_table_path("gold_daily_trips", data_root))
    stations_path = _table_path("gold_station_traffic", data_root)
    stations = load_csv(stations_path) if stations_path.exists() else None

    suite = SuiteResult()
    for rows, contract, table in (
        (silver, silver_contract, "silver_trips"),
        (daily, gold_contract, "gold_daily_trips"),
    ):
        suite.results.extend(check_schema(table, rows, contract))
        suite.results.extend(check_row_count(table, rows, contract))
        suite.results.extend(check_null_rates(table, rows, contract))
        suite.results.extend(check_accepted_values(table, rows, contract))
        suite.results.extend(check_freshness(table, rows, contract, as_of=as_of))
    suite.results.extend(check_referential(silver, daily, stations))

    md, page = write_reports(suite)
    print(f"quality: {'PASS' if suite.passed else 'FAIL'} ({len(suite.results)} checks)")
    print(f"wrote {md}")
    print(f"wrote {page}")
    return suite
