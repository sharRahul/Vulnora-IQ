from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_diffs(input_dir: str | Path, pattern: str = "*diff.json") -> list[dict[str, Any]]:
    diffs: list[dict[str, Any]] = []
    for path in sorted(Path(input_dir).glob(pattern)):
        data = json.loads(path.read_text(encoding="utf-8"))
        if "finding_count_delta" in data:
            data["_path"] = str(path)
            diffs.append(data)
    return diffs


def build_summary(diffs: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "diff_count": len(diffs),
        "regression_count": sum(1 for item in diffs if item.get("has_regression") is True),
        "total_finding_delta": sum(int(item.get("finding_count_delta", 0)) for item in diffs),
        "policy_status_change_count": sum(1 for item in diffs if item.get("policy_status_changed") is True),
        "diffs": [
            {
                "path": item.get("_path"),
                "baseline_report": item.get("baseline_report"),
                "current_report": item.get("current_report"),
                "finding_count_delta": item.get("finding_count_delta"),
                "policy_status_changed": item.get("policy_status_changed"),
                "has_regression": item.get("has_regression"),
            }
            for item in diffs
        ],
    }


def write_markdown(summary: dict[str, Any], output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Report Diff Trend Dashboard",
        "",
        "| Metric | Value |",
        "| --- | --- |",
        f"| Diff count | `{summary['diff_count']}` |",
        f"| Regression count | `{summary['regression_count']}` |",
        f"| Total finding delta | `{summary['total_finding_delta']}` |",
        f"| Policy status changes | `{summary['policy_status_change_count']}` |",
        "",
        "## Diffs",
        "",
        "| Diff | Finding delta | Policy changed | Regression |",
        "| --- | --- | --- | --- |",
    ]
    for item in summary["diffs"]:
        lines.append(f"| `{item.get('path')}` | {item.get('finding_count_delta')} | {item.get('policy_status_changed')} | {item.get('has_regression')} |")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output


def write_html(summary: dict[str, Any], output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = "".join(
        f"<tr><td>{item.get('path')}</td><td>{item.get('finding_count_delta')}</td><td>{item.get('policy_status_changed')}</td><td>{item.get('has_regression')}</td></tr>"
        for item in summary["diffs"]
    )
    html = f"""<!doctype html>
<html lang=\"en\">
<head><meta charset=\"utf-8\"><title>Report Diff Trend Dashboard</title></head>
<body>
<h1>Report Diff Trend Dashboard</h1>
<ul>
<li>Diff count: {summary['diff_count']}</li>
<li>Regression count: {summary['regression_count']}</li>
<li>Total finding delta: {summary['total_finding_delta']}</li>
<li>Policy status changes: {summary['policy_status_change_count']}</li>
</ul>
<table border=\"1\"><thead><tr><th>Diff</th><th>Finding delta</th><th>Policy changed</th><th>Regression</th></tr></thead><tbody>{rows}</tbody></table>
</body></html>
"""
    output.write_text(html, encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Build trend dashboards from report diff JSON files.")
    parser.add_argument("--input-dir", default="reports/output")
    parser.add_argument("--markdown-output", default="reports/output/diff-trend-dashboard.md")
    parser.add_argument("--html-output", default="reports/output/diff-trend-dashboard.html")
    args = parser.parse_args()
    summary = build_summary(load_diffs(args.input_dir))
    markdown = write_markdown(summary, args.markdown_output)
    html = write_html(summary, args.html_output)
    print(f"Diff trend dashboard written to {markdown} and {html}")


if __name__ == "__main__":
    main()
