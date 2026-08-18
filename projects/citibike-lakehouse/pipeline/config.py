from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW_CSV = DATA / "raw" / "citibike_trips.csv"
BRONZE_DIR = DATA / "bronze"
SILVER_DIR = DATA / "silver"
GOLD_DIR = DATA / "gold"
