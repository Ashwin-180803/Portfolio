from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

from quality.run import run


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="quality")
    sub = parser.add_subparsers(dest="command", required=True)
    run_parser = sub.add_parser("run", help="Validate tables against contracts")
    run_parser.add_argument("--data-root", type=Path, default=None)
    run_parser.add_argument("--as-of", type=str, default=None, help="ISO timestamp for freshness")
    args = parser.parse_args(argv)

    as_of = datetime.fromisoformat(args.as_of) if args.as_of else None
    suite = run(data_root=args.data_root, as_of=as_of)
    sys.exit(0 if suite.passed else 1)


if __name__ == "__main__":
    main()
