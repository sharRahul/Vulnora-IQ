from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class PolicyTrend:
    report_count: int
    policy_status_counts: dict[str, int]
    per_policy_status_counts: dict[str, dict[str, int]]
    target_profile_runs: list[dict[str, Any]]


def load_reports(input_dir: str | Path, pattern: str = "*.json") -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    for path in sorted(Path(input_dir).glob(pattern)):
        if path.name.endswith("diff.json") or path.name.endswith("summary.json"):
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if "policy_results" in data:
            data["_path"] = str(path)
            reports.append(data)
    return reports


def build_policy_trend(reports: list[dict[str, Any]]) -> PolicyTrend:
    overall = Counter(str(report.get("policy_status", "unknown")) for report in reports)
    per_policy: dict[str, Counter] = defaultdict(Counter)
    runs: list[dict[str, Any]] = []
    for report in reports:
        runs.append(
            {
                "path": report.get("_path"),
                "target": report.get("target"),
                "profile": report.get("profile"),
                "policy_status": report.get("policy_status"),
                "finding_count": report.get("finding_count"),
                "highest_severity": report.get("highest_severity"),
            }
        )
        for policy in report.get("policy_results", []):
            per_policy[str(policy.get("policy_id"))][str(policy.get("status", "unknown"))] += 1
    return PolicyTrend(
        report_count=len(reports),
        policy_status_counts=dict(overall),
        per_policy_status_counts={key: dict(value) for key, value in sorted(per_policy.items())},
        target_profile_runs=runs,
    )


def write_json(trend: PolicyTrend, output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(asdict(trend), indent=2, sort_keys=True), encoding="utf-8")
    return output


def write_markdown(trend: PolicyTrend, output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Policy Result Trend",
        "",
        f"Reports analysed: `{trend.report_count}`",
        "",
        "## Overall policy status counts",
        "",
        "| Status | Count |",
        "| --- | --- |",
    ]
    for status, count in sorted(trend.policy_status_counts.items()):
        lines.append(f"| {status} | {count} |")
    lines.extend(["", "## Per-policy status counts", "", "| Policy | Status counts |", "| --- | --- |"])
    for policy_id, counts in trend.per_policy_status_counts.items():
        lines.append(f"| {policy_id} | `{json.dumps(counts, sort_keys=True)}` |")
    lines.extend(["", "## Runs", "", "| Target | Profile | Policy status | Findings | Highest severity |", "| --- | --- | --- | --- | --- |"])
    for run in trend.target_profile_runs:
        lines.append(f"| {run.get('target')} | {run.get('profile')} | {run.get('policy_status')} | {run.get('finding_count')} | {run.get('highest_severity')} |")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Build policy result trends from JSON reports.")
    parser.add_argument("--input-dir", default="reports/output")
    parser.add_argument("--pattern", default="*.json")
    parser.add_argument("--json-output", default="reports/output/policy-trend.json")
    parser.add_argument("--markdown-output", default="reports/output/policy-trend.md")
    args = parser.parse_args()
    trend = build_policy_trend(load_reports(args.input_dir, args.pattern))
    json_output = write_json(trend, args.json_output)
    markdown_output = write_markdown(trend, args.markdown_output)
    print(f"Policy trend written to {json_output} and {markdown_output}")


if __name__ == "__main__":
    main()
