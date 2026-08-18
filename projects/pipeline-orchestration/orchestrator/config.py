from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT.parent
LAKEHOUSE = PROJECTS / "citibike-lakehouse"
WAREHOUSE = PROJECTS / "citibike-dbt-warehouse"
QUALITY = PROJECTS / "data-quality-framework"
STATUS = ROOT / "reports" / "last_run.json"
