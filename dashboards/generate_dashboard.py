from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


class DashboardGenerator:
    """Builds a lightweight Markdown dashboard from a structured report."""

    def generate_from_report(self, report: dict[str, Any], output_path: str | Path) -> Path:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        lines = [
            f"# VulnoraIQ Assessment Dashboard - {report.get('target', 'unknown')}",
            "",
            "## Summary",
            "",
            "| Metric | Value |",
            "| --- | --- |",
            f"| Profile | `{report.get('profile', '')}` |",
            f"| Findings | `{report.get('finding_count', 0)}` |",
            f"| Highest severity | `{report.get('highest_severity', 'info')}` |",
            f"| Policy status | `{report.get('policy_status', 'pass')}` |",
            "",
            "## Severity distribution",
            "",
            "| Severity | Count |",
            "| --- | --- |",
        ]

        for severity, count in sorted(report.get("severity_counts", {}).items()):
            lines.append(f"| {severity} | {count} |")

        lines.extend([
            "",
            "## OWASP coverage",
            "",
            "| OWASP category | Findings |",
            "| --- | --- |",
        ])
        for owasp_id, count in sorted(report.get("owasp_counts", {}).items()):
            lines.append(f"| {owasp_id} | {count} |")

        lines.extend([
            "",
            "## Policy status",
            "",
            "| Policy | Status | Decision | Message |",
            "| --- | --- | --- | --- |",
        ])
        for policy in report.get("policy_results", []):
            message = str(policy.get("message", "")).replace("|", "\|")
            lines.append(
                f"| {policy.get('policy_id', '')} | {policy.get('status', '')} | {policy.get('decision', '')} | {message} |"
            )

        lines.extend([
            "",
            "## Top findings",
            "",
            "| Severity | Score | Title | OWASP | Component |",
            "| --- | --- | --- | --- | --- |",
        ])
        findings = sorted(report.get("findings", []), key=lambda item: item.get("score") or 0, reverse=True)
        for finding in findings[:10]:
            title = str(finding.get("title", "")).replace("|", "\|")
            component = str(finding.get("affected_component", "")).replace("|", "\|")
            lines.append(
                f"| {finding.get('severity', '')} | {finding.get('score', '')} | {title} | {finding.get('owasp_id', '')} | {component} |"
            )

        output.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a Markdown dashboard from a JSON assessment report.")
    parser.add_argument("--report", required=True, help="Input JSON report path.")
    parser.add_argument("--output", default="reports/output/dashboard.md", help="Output Markdown dashboard path.")
    args = parser.parse_args()

    report = json.loads(Path(args.report).read_text(encoding="utf-8"))
    output = DashboardGenerator().generate_from_report(report, args.output)
    print(f"Dashboard written to {output}")


if __name__ == "__main__":
    main()
