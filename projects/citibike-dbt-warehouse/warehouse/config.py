from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED_CSV = ROOT / "seeds" / "trips.csv"
MODELS_DIR = ROOT / "models"
DB_PATH = ROOT / "warehouse.duckdb"
DOCS_PATH = ROOT / "target" / "catalog.md"

MODEL_ORDER = [
    "stg_trips",
    "dim_date",
    "dim_station",
    "fct_trips",
    "rpt_daily_trips",
]
