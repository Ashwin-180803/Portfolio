from __future__ import annotations

from pipeline.bronze import land_bronze
from pipeline.gold import to_gold
from pipeline.silver import to_silver


def run() -> None:
    bronze = land_bronze()
    silver = to_silver(bronze)
    gold = to_gold(silver)
    print(
        f"done: bronze={bronze.height} silver={silver.height} "
        f"gold_tables={len(gold)}"
    )


def main() -> None:
    run()
