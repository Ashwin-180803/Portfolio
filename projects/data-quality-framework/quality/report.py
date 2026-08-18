from __future__ import annotations

import html
from pathlib import Path

from quality.checks import SuiteResult
from quality.config import REPORTS


def write_reports(suite: SuiteResult) -> tuple[Path, Path]:
    REPORTS.mkdir(parents=True, exist_ok=True)
    md = REPORTS / "quality_report.md"
    page = REPORTS / "quality_report.html"
    status = "PASS" if suite.passed else "FAIL"
    lines = [f"# Data quality report — {status}", "", "| Check | Table | Result | Detail |", "| --- | --- | --- | --- |"]
    rows = []
    for item in suite.results:
        mark = "PASS" if item.passed else "FAIL"
        lines.append(f"| `{item.name}` | `{item.table}` | **{mark}** | {item.detail} |")
        rows.append(
            "<tr>"
            f"<td><code>{html.escape(item.name)}</code></td>"
            f"<td><code>{html.escape(item.table)}</code></td>"
            f"<td>{mark}</td>"
            f"<td>{html.escape(item.detail)}</td>"
            "</tr>"
        )
    md.write_text("\n".join(lines) + "\n")
    page.write_text(
        "<!doctype html><html><head><meta charset='utf-8'><title>Quality report</title>"
        "<style>body{font-family:sans-serif;background:#0b0f14;color:#e8eef4;padding:32px}"
        "table{border-collapse:collapse;width:100%}td,th{border:1px solid #243041;padding:8px;text-align:left}"
        ".FAIL{color:#f0c14b}</style></head><body>"
        f"<h1>Data quality report — {status}</h1>"
        "<table><thead><tr><th>Check</th><th>Table</th><th>Result</th><th>Detail</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table></body></html>"
    )
    return md, page
