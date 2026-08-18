from __future__ import annotations

import re
from pathlib import Path

import duckdb

from warehouse.config import DB_PATH, DOCS_PATH, MODEL_ORDER, MODELS_DIR, ROOT, SEED_CSV

REF = re.compile(r"{{\s*ref\(['\"]([^'\"]+)['\"]\)\s*}}")


def _sql_for(name: str) -> str:
    matches = list(MODELS_DIR.rglob(f"{name}.sql"))
    if not matches:
        raise FileNotFoundError(name)
    raw = matches[0].read_text()
    return REF.sub(lambda m: m.group(1), raw)


def _materialize(con: duckdb.DuckDBPyConnection, name: str, sql: str) -> None:
    kind = "view" if name.startswith("stg_") else "table"
    con.execute(f"drop view if exists {name}")
    con.execute(f"drop table if exists {name}")
    con.execute(f"create {kind} {name} as {sql}")
    count = con.execute(f"select count(*) from {name}").fetchone()[0]
    print(f"ok {kind:5} {name:16} {count} rows")


def _test_unique(con: duckdb.DuckDBPyConnection, table: str, column: str) -> None:
    dupes = con.execute(
        f"select count(*) from (select {column} from {table} group by 1 having count(*) > 1)"
    ).fetchone()[0]
    if dupes:
        raise AssertionError(f"{table}.{column} unique failed ({dupes} duplicate keys)")


def _test_not_null(con: duckdb.DuckDBPyConnection, table: str, column: str) -> None:
    nulls = con.execute(f"select count(*) from {table} where {column} is null").fetchone()[0]
    if nulls:
        raise AssertionError(f"{table}.{column} not_null failed ({nulls} nulls)")


def _test_accepted(con: duckdb.DuckDBPyConnection, table: str, column: str, values: list[str]) -> None:
    quoted = ", ".join(f"'{v}'" for v in values)
    bad = con.execute(
        f"select count(*) from {table} where {column} not in ({quoted})"
    ).fetchone()[0]
    if bad:
        raise AssertionError(f"{table}.{column} accepted_values failed ({bad} rows)")


def _test_rel(con: duckdb.DuckDBPyConnection, table: str, column: str, to: str, field: str) -> None:
    orphans = con.execute(
        f"select count(*) from {table} t left join {to} d on t.{column} = d.{field} where d.{field} is null"
    ).fetchone()[0]
    if orphans:
        raise AssertionError(f"{table}.{column} → {to}.{field} relationship failed ({orphans} orphans)")


def run_tests(con: duckdb.DuckDBPyConnection) -> None:
    _test_unique(con, "stg_trips", "ride_id")
    _test_not_null(con, "stg_trips", "ride_id")
    _test_not_null(con, "stg_trips", "member_casual")
    _test_accepted(con, "stg_trips", "member_casual", ["member", "casual"])
    _test_not_null(con, "stg_trips", "rideable_type")
    _test_accepted(con, "stg_trips", "rideable_type", ["classic_bike", "electric_bike"])
    _test_not_null(con, "stg_trips", "duration_sec")
    _test_not_null(con, "stg_trips", "start_station_id")
    _test_not_null(con, "stg_trips", "end_station_id")
    _test_unique(con, "dim_date", "trip_date")
    _test_not_null(con, "dim_date", "trip_date")
    _test_unique(con, "dim_station", "station_id")
    _test_not_null(con, "dim_station", "station_id")
    _test_unique(con, "fct_trips", "ride_id")
    _test_not_null(con, "fct_trips", "ride_id")
    _test_not_null(con, "fct_trips", "trip_date")
    _test_rel(con, "fct_trips", "trip_date", "dim_date", "trip_date")
    _test_not_null(con, "fct_trips", "start_station_id")
    _test_rel(con, "fct_trips", "start_station_id", "dim_station", "station_id")
    _test_not_null(con, "fct_trips", "end_station_id")
    _test_rel(con, "fct_trips", "end_station_id", "dim_station", "station_id")
    _test_unique(con, "rpt_daily_trips", "trip_date")
    _test_not_null(con, "rpt_daily_trips", "trip_date")
    print("ok tests   23 passed")


def write_docs(con: duckdb.DuckDBPyConnection) -> None:
    DOCS_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# citibike warehouse catalog", ""]
    for name in ["trips", *MODEL_ORDER]:
        cols = con.execute(
            f"select column_name, data_type from information_schema.columns where table_name = '{name}' order by ordinal_position"
        ).fetchall()
        n = con.execute(f"select count(*) from {name}").fetchone()[0]
        lines.append(f"## {name} ({n} rows)")
        for col, dtype in cols:
            lines.append(f"- `{col}` {dtype}")
        lines.append("")
    DOCS_PATH.write_text("\n".join(lines))
    print(f"ok docs    {DOCS_PATH.relative_to(ROOT)}")


def run(seed_csv: Path | None = None) -> None:
    csv_path = seed_csv or SEED_CSV
    if DB_PATH.exists():
        DB_PATH.unlink()
    con = duckdb.connect(str(DB_PATH))
    con.execute(
        f"create table trips as select * from read_csv_auto('{csv_path.as_posix()}', header=true)"
    )
    n = con.execute("select count(*) from trips").fetchone()[0]
    print(f"ok seed   trips            {n} rows")
    for name in MODEL_ORDER:
        _materialize(con, name, _sql_for(name))
    run_tests(con)
    write_docs(con)
    con.close()
    print(f"done → {DB_PATH.name}")


def main() -> None:
    run()
