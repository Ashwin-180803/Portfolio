from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from quality.config import CONTRACTS


def load_contract(name: str) -> dict[str, Any]:
    path = CONTRACTS / f"{name}.json"
    return json.loads(path.read_text())


def list_contracts() -> list[Path]:
    return sorted(CONTRACTS.glob("*.json"))
