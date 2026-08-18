from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone

from orchestrator.config import LAKEHOUSE, QUALITY, STATUS, WAREHOUSE


def _python(project) -> str:
    venv = project / ".venv" / "bin" / "python"
    return str(venv) if venv.exists() else sys.executable


def _run(name: str, argv: list[str], cwd, extra_env: dict[str, str] | None = None) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(cwd) + os.pathsep + env.get("PYTHONPATH", "")
    if extra_env:
        env.update(extra_env)
    print(f"→ {name}: {' '.join(argv)}", flush=True)
    subprocess.run(argv, cwd=cwd, env=env, check=True)


def run() -> None:
    STATUS.parent.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc)

    _run("ingest_lakehouse", [_python(LAKEHOUSE), "-m", "pipeline"], cwd=LAKEHOUSE)

    silver = LAKEHOUSE / "data" / "silver" / "trips.csv"
    seed = WAREHOUSE / "seeds" / "trips.csv"
    shutil.copyfile(silver, seed)
    _run("run_dbt", [_python(WAREHOUSE), "-m", "warehouse"], cwd=WAREHOUSE)

    _run(
        "run_quality",
        [
            _python(QUALITY),
            "-m",
            "quality",
            "run",
            "--data-root",
            str(LAKEHOUSE / "data"),
        ],
        cwd=QUALITY,
    )

    payload = {
        "dag": "citibike_daily",
        "status": "success",
        "started_at": started.isoformat(),
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "tasks": ["ingest_lakehouse", "run_dbt", "run_quality", "publish_status"],
    }
    STATUS.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"→ publish_status: {STATUS}")
    print("done")


def main() -> None:
    run()
