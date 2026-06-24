from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from core.scanner import Scanner
from dashboards.generate_dashboard import DashboardGenerator
from dashboards.html_dashboard import HtmlDashboardGenerator
from integrations.target_adapters import connectivity_check
from reports.json_report_generator import JsonReportGenerator
from reports.report_generator import MarkdownReportGenerator
from reports.sarif_report_generator import SarifReportGenerator


def _load_targets() -> dict:
    path = Path("config/targets.yaml")
    return (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("targets", {})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run authorised AI agent and LLM application assessments.")
    sub = parser.add_subparsers(dest="command")
    targets = sub.add_parser("targets", help="Manage configured targets")
    tsub = targets.add_subparsers(dest="targets_command")
    tsub.add_parser("list", help="List configured targets")
    val = tsub.add_parser("validate", help="Validate target connectivity and response mapping")
    val.add_argument("--target", required=True)
    scan = sub.add_parser("scan", help="Run a scan")
    add_scan_args(scan)
    add_scan_args(parser)
    return parser


def add_scan_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--target", default="demo", help="Target name from config/targets.yaml. Default: demo")
    parser.add_argument("--profile", default="baseline", help="Assessment profile from config/attack_profiles.yaml. Default: baseline")
    parser.add_argument("--output", default="reports/output/scan-report.md", help="Markdown report output path.")
    parser.add_argument("--json-output", default="reports/output/scan-report.json", help="Structured JSON report output path.")
    parser.add_argument("--sarif-output", default="reports/output/scan-report.sarif", help="SARIF-style report output path.")
    parser.add_argument("--dashboard-output", default="reports/output/dashboard.md", help="Markdown dashboard output path.")
    parser.add_argument("--html-dashboard-output", default="reports/output/dashboard.html", help="HTML dashboard output path.")
    parser.add_argument("--authorised", action="store_true", help="Required for non-demo targets you own or are explicitly authorised to assess.")


def run_scan(args: argparse.Namespace) -> None:
    scanner = Scanner(config_dir=Path("config"))
    result = scanner.scan(target_name=args.target, profile_name=args.profile, authorised=args.authorised)
    markdown_output = MarkdownReportGenerator().generate(result, args.output)
    json_output = JsonReportGenerator().generate(result, args.json_output)
    sarif_output = SarifReportGenerator().generate(result, args.sarif_output)
    report_data = json.loads(Path(json_output).read_text(encoding="utf-8"))
    dashboard_output = DashboardGenerator().generate_from_report(report_data, args.dashboard_output)
    html_dashboard_output = HtmlDashboardGenerator().generate_from_report(report_data, args.html_dashboard_output)
    print(f"Assessment complete: {result.finding_count} findings. Policy status: {result.policy_status}. Reports written to {markdown_output}, {json_output}, {sarif_output}, {dashboard_output}, and {html_dashboard_output}")


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "targets":
        targets = _load_targets()
        if args.targets_command == "list":
            for name, cfg in targets.items():
                print(f"{name}\t{cfg.get('type')}\t{cfg.get('environment', 'unknown')}\t{cfg.get('base_url') or cfg.get('endpoint')}")
            return
        if args.targets_command == "validate":
            if args.target not in targets:
                raise SystemExit(f"Unknown target: {args.target}")
            print(json.dumps(connectivity_check(args.target, targets[args.target]), indent=2, default=str))
            return
    run_scan(args)


if __name__ == "__main__":
    main()
