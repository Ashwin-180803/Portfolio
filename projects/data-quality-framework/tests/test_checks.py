from datetime import datetime, timezone
from pathlib import Path

from quality.checks import check_freshness, check_null_rates, check_row_count, check_schema, load_csv
from quality.contracts import load_contract
from quality.run import run

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def test_fixtures_pass_the_suite():
    suite = run()
    assert suite.passed
    assert any(item.name == "schema" for item in suite.results)


def test_row_count_fails_when_empty():
    contract = load_contract("silver_trips")
    result = check_row_count("silver_trips", [], contract)[0]
    assert result.passed is False


def test_schema_fails_when_column_missing():
    contract = load_contract("silver_trips")
    result = check_schema("silver_trips", [{"ride_id": "x"}], contract)[0]
    assert result.passed is False
    assert "missing columns" in result.detail


def test_null_rate_fails_when_required_column_empty():
    contract = {"null_rate_max": {"ride_id": 0}}
    rows = [{"ride_id": None}, {"ride_id": "a"}]
    result = check_null_rates("silver_trips", rows, contract)[0]
    assert result.passed is False


def test_freshness_fails_when_as_of_is_far_ahead():
    contract = load_contract("silver_trips")
    rows = load_csv(FIXTURES / "silver_trips.csv")[:5]
    future = datetime(2030, 1, 1, tzinfo=timezone.utc)
    result = check_freshness("silver_trips", rows, contract, as_of=future)[0]
    assert result.passed is False
