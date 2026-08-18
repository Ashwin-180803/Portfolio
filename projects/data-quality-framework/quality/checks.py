from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class CheckResult:
    name: str
    table: str
    passed: bool
    detail: str


@dataclass
class SuiteResult:
    results: list[CheckResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(item.passed for item in self.results)


def load_csv(path: Path) -> list[dict[str, str | None]]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        rows: list[dict[str, str | None]] = []
        for raw in reader:
            rows.append({key: (value if value not in (None, "") else None) for key, value in raw.items()})
        return rows


def parse_timestamp(value: str) -> datetime:
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            parsed = datetime.strptime(value, fmt)
            return parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    raise ValueError(f"unparsed timestamp: {value}")


def check_schema(table: str, rows: list[dict[str, str | None]], contract: dict[str, Any]) -> list[CheckResult]:
    expected = set(contract["columns"])
    actual = set(rows[0].keys()) if rows else expected
    missing = sorted(expected - actual)
    return [
        CheckResult(
            name="schema",
            table=table,
            passed=not missing,
            detail="ok" if not missing else f"missing columns: {missing}",
        )
    ]


def check_row_count(table: str, rows: list[dict[str, str | None]], contract: dict[str, Any]) -> list[CheckResult]:
    n = len(rows)
    lo = contract.get("min_rows", 0)
    hi = contract.get("max_rows", 10**12)
    ok = lo <= n <= hi
    return [
        CheckResult(
            name="row_count",
            table=table,
            passed=ok,
            detail=f"{n} rows (allowed {lo}-{hi})",
        )
    ]


def check_null_rates(table: str, rows: list[dict[str, str | None]], contract: dict[str, Any]) -> list[CheckResult]:
    results: list[CheckResult] = []
    n = max(len(rows), 1)
    for column, ceiling in contract.get("null_rate_max", {}).items():
        rate = sum(1 for row in rows if row.get(column) is None) / n
        results.append(
            CheckResult(
                name=f"null_rate.{column}",
                table=table,
                passed=rate <= ceiling,
                detail=f"{rate:.2%} (max {ceiling:.0%})",
            )
        )
    return results


def check_accepted_values(table: str, rows: list[dict[str, str | None]], contract: dict[str, Any]) -> list[CheckResult]:
    results: list[CheckResult] = []
    for column, allowed in contract.get("accepted_values", {}).items():
        allowed_set = set(allowed)
        bad = sum(1 for row in rows if row.get(column) not in allowed_set)
        results.append(
            CheckResult(
                name=f"accepted_values.{column}",
                table=table,
                passed=bad == 0,
                detail="ok" if bad == 0 else f"{bad} rows outside {sorted(allowed_set)}",
            )
        )
    return results


def check_freshness(
    table: str,
    rows: list[dict[str, str | None]],
    contract: dict[str, Any],
    as_of: datetime | None = None,
) -> list[CheckResult]:
    column = contract.get("freshness_column")
    if not column:
        return []
    timestamps = [parse_timestamp(row[column]) for row in rows if row.get(column)]
    if not timestamps:
        return [CheckResult(name="freshness", table=table, passed=False, detail="no timestamps")]
    latest = max(timestamps)
    reference = as_of or latest
    lag_days = (reference.date() - latest.date()).days
    ceiling = contract.get("max_lag_days", 7)
    return [
        CheckResult(
            name="freshness",
            table=table,
            passed=lag_days <= ceiling,
            detail=f"latest={latest.date()} lag={lag_days}d (max {ceiling}d)",
        )
    ]


def check_referential(
    silver: list[dict[str, str | None]],
    daily: list[dict[str, str | None]],
    stations: list[dict[str, str | None]] | None = None,
) -> list[CheckResult]:
    results: list[CheckResult] = []
    silver_dates = {parse_timestamp(row["started_at"]).date() for row in silver if row.get("started_at")}
    gold_dates = {date.fromisoformat(row["trip_date"][:10]) for row in daily if row.get("trip_date")}
    missing = sorted(silver_dates - gold_dates)
    results.append(
        CheckResult(
            name="referential.daily_dates",
            table="gold_daily_trips",
            passed=not missing,
            detail="ok" if not missing else f"dates in silver missing from gold: {missing[:5]}",
        )
    )
    if stations is not None:
        station_ids = {row.get("station_id") for row in stations}
        orphans = sum(
            1
            for row in silver
            if row.get("start_station_id") not in station_ids or row.get("end_station_id") not in station_ids
        )
        results.append(
            CheckResult(
                name="referential.stations",
                table="silver_trips",
                passed=orphans == 0,
                detail="ok" if orphans == 0 else f"{orphans} trips with unknown station_id",
            )
        )
    return results
