from __future__ import annotations

import argparse
from pathlib import Path

from core.scanner import Scanner
from dashboards.generate_dashboard import DashboardGenerator
from reports.json_report_generator import JsonReportGenerator
from reports.report_generator import MarkdownReportGenerator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run an authorised LLM application assessment.")
    parser.add_argument("--target", default="demo", help="Target name from config/targets.yaml. Default: demo")
    parser.add_argument("--profile", default="baseline", help="Assessment profile from config/attack_profiles.yaml. Default: baseline")
    parser.add_argument("--output", default="reports/output/scan-report.md", help="Markdown report output path.")
    parser.add_argument("--json-output", default="reports/output/scan-report.json", help="Structured JSON report output path.")
    parser.add_argument("--dashboard-output", default="reports/output/dashboard.md", help="Markdown dashboard output path.")
    parser.add_argument(
        "--authorised",
        action="store_true",
        help="Required for configured targets outside the demo mode. Use only where you have permission.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    scanner = Scanner(config_dir=Path("config"))
    result = scanner.scan(target_name=args.target, profile_name=args.profile, authorised=args.authorised)

    markdown_output = MarkdownReportGenerator().generate(result, args.output)
    json_output = JsonReportGenerator().generate(result, args.json_output)

    import json

    report_data = json.loads(Path(json_output).read_text(encoding="utf-8"))
    dashboard_output = DashboardGenerator().generate_from_report(report_data, args.dashboard_output)

    print(
        "Assessment complete: "
        f"{result.finding_count} findings. "
        f"Policy status: {result.policy_status}. "
        f"Reports written to {markdown_output}, {json_output}, and {dashboard_output}"
    )


if __name__ == "__main__":
    main()
