from __future__ import annotations

import argparse
import html
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from core.scanner import Scanner
from dashboards.generate_dashboard import DashboardGenerator
from dashboards.html_dashboard import HtmlDashboardGenerator
from reports.json_report_generator import JsonReportGenerator
from reports.report_generator import MarkdownReportGenerator
from reports.sarif_report_generator import SarifReportGenerator

PRODUCTION_READY_MARKER = "authorised_production_assessment_testing_ready"


@dataclass(slots=True)
class FunctionalTestSummary:
    status: str
    target: str
    profile: str
    output_dir: str
    screenshot_path: str
    generated_files: list[str]
    checks: dict[str, str] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DashboardExampleSvgGenerator:
    """Creates a deterministic README-friendly dashboard example from a report."""

    def generate(self, report: dict[str, Any], output_path: str | Path) -> Path:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        findings = report.get("findings", [])
        target = html.escape(str(report.get("target", "demo")))
        profile = html.escape(str(report.get("profile", "baseline")))
        policy_status = html.escape(str(report.get("policy_status", "unknown")).upper())
        highest = html.escape(str(report.get("highest_severity", "info")).upper())
        production_profile = html.escape(str(report.get("production_detection_profile", "authorised_production_assessment_v1")))
        rows = []
        y = 395
        for finding in findings[:5]:
            title = html.escape(str(finding.get("title", "Untitled finding"))[:76])
            severity = html.escape(str(finding.get("severity", "info")).upper())
            owasp = html.escape(str(finding.get("owasp_id", "UNMAPPED")))
            summary = finding.get("evidence", {}).get("production_detection_status_summary", {})
            prod = f"P:{summary.get('pass', 0)} W:{summary.get('warn', 0)} F:{summary.get('fail', 0)}"
            rows.append(f'<text x="72" y="{y}" class="row">{severity} · {owasp} · {html.escape(prod)} · {title}</text>')
            y += 32
        if not rows:
            rows.append('<text x="72" y="395" class="row">INFO · No findings generated in this demo run</text>')
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720" role="img" aria-label="VulnoraIQ dashboard example">
  <rect width="1280" height="720" fill="#0f172a"/>
  <rect x="40" y="36" width="1200" height="648" rx="28" fill="#111827" stroke="#334155"/>
  <style>
    .title {{ fill: #f9fafb; font: 700 42px system-ui, -apple-system, Segoe UI, sans-serif; }}
    .subtitle {{ fill: #cbd5e1; font: 500 18px system-ui, -apple-system, Segoe UI, sans-serif; }}
    .card-title {{ fill: #94a3b8; font: 600 15px system-ui, -apple-system, Segoe UI, sans-serif; text-transform: uppercase; }}
    .card-value {{ fill: #f8fafc; font: 800 32px system-ui, -apple-system, Segoe UI, sans-serif; }}
    .section {{ fill: #e5e7eb; font: 700 24px system-ui, -apple-system, Segoe UI, sans-serif; }}
    .row {{ fill: #d1d5db; font: 500 16px system-ui, -apple-system, Segoe UI, sans-serif; }}
    .muted {{ fill: #9ca3af; font: 500 15px system-ui, -apple-system, Segoe UI, sans-serif; }}
  </style>
  <text x="72" y="96" class="title">VulnoraIQ Assessment Dashboard</text>
  <text x="72" y="132" class="subtitle">Authorised production-assessment test path · target {target} · profile {profile}</text>
  <rect x="72" y="170" width="230" height="120" rx="18" fill="#020617" stroke="#374151"/>
  <text x="96" y="212" class="card-title">Findings</text>
  <text x="96" y="258" class="card-value">{len(findings)}</text>
  <rect x="324" y="170" width="250" height="120" rx="18" fill="#020617" stroke="#374151"/>
  <text x="348" y="212" class="card-title">Highest severity</text>
  <text x="348" y="258" class="card-value">{highest}</text>
  <rect x="596" y="170" width="250" height="120" rx="18" fill="#020617" stroke="#374151"/>
  <text x="620" y="212" class="card-title">Policy status</text>
  <text x="620" y="258" class="card-value">{policy_status}</text>
  <rect x="868" y="170" width="300" height="120" rx="18" fill="#020617" stroke="#374151"/>
  <text x="892" y="212" class="card-title">Detector profile</text>
  <text x="892" y="248" class="subtitle">{production_profile[:28]}</text>
  <text x="72" y="350" class="section">Top findings with production detector counts</text>
  {''.join(rows)}
  <rect x="72" y="560" width="1096" height="72" rx="16" fill="#020617" stroke="#374151"/>
  <text x="96" y="592" class="muted">Generated from scripts/run_functional_test.py using the safe local demo assessment.</text>
  <text x="96" y="618" class="muted">Use only for authorised security-assessment testing; tester review is still required.</text>
</svg>
'''
        output.write_text(svg, encoding="utf-8")
        return output


def run_functional_test(
    output_dir: str | Path = "reports/output/functional-test",
    screenshot_path: str | Path = "docs/assets/vulnoraiq-dashboard-example.svg",
) -> FunctionalTestSummary:
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    markdown_path = output_root / "functional-report.md"
    json_path = output_root / "functional-report.json"
    sarif_path = output_root / "functional-report.sarif"
    dashboard_path = output_root / "functional-dashboard.md"
    html_dashboard_path = output_root / "functional-dashboard.html"
    summary_path = output_root / "functional-test-summary.json"

    result = Scanner(config_dir=Path("config")).scan(target_name="demo", profile_name="baseline", authorised=False)
    markdown_output = MarkdownReportGenerator().generate(result, markdown_path)
    json_output = JsonReportGenerator().generate(result, json_path)
    sarif_output = SarifReportGenerator().generate(result, sarif_path)
    report_data = json.loads(Path(json_output).read_text(encoding="utf-8"))
    dashboard_output = DashboardGenerator().generate_from_report(report_data, dashboard_path)
    html_output = HtmlDashboardGenerator().generate_from_report(report_data, html_dashboard_path)
    screenshot_output = DashboardExampleSvgGenerator().generate(report_data, screenshot_path)

    generated = [str(markdown_output), str(json_output), str(sarif_output), str(dashboard_output), str(html_output), str(screenshot_output), str(summary_path)]
    checks: dict[str, str] = {}
    errors: list[str] = []

    for path in generated[:-1]:
        file_path = Path(path)
        checks[f"non_empty:{file_path.name}"] = "pass" if file_path.exists() and file_path.stat().st_size > 0 else "fail"
        if checks[f"non_empty:{file_path.name}"] == "fail":
            errors.append(f"Missing or empty output: {file_path}")

    required_fields = ["target", "profile", "finding_count", "policy_status", "metadata", "findings", "policy_results"]
    missing_fields = [field for field in required_fields if field not in report_data]
    checks["json_required_fields"] = "pass" if not missing_fields else "fail"
    if missing_fields:
        errors.append(f"Functional JSON report missing fields: {', '.join(missing_fields)}")

    checks["demo_baseline_scope"] = "pass" if report_data.get("target") == "demo" and report_data.get("profile") == "baseline" else "fail"
    if checks["demo_baseline_scope"] == "fail":
        errors.append("Functional run did not execute demo/baseline scope.")

    metadata = report_data.get("metadata", {})
    oracle_coverage = metadata.get("owasp_oracle_coverage", {})
    production_coverage = metadata.get("production_owasp_detection", {})
    checks["owasp_category_count"] = "pass" if oracle_coverage.get("owasp_category_count") == 10 else "fail"
    checks["production_owasp_detector_count"] = "pass" if production_coverage.get("covered_category_count") == 10 else "fail"
    checks["production_validation_marker"] = "pass" if metadata.get("production_validation_status") == PRODUCTION_READY_MARKER else "fail"
    if checks["owasp_category_count"] == "fail":
        errors.append("OWASP oracle coverage does not report all 10 categories.")
    if checks["production_owasp_detector_count"] == "fail":
        errors.append("Production OWASP detector coverage does not report all 10 categories.")
    if checks["production_validation_marker"] == "fail":
        errors.append("Production assessment readiness marker is missing or incorrect.")

    html_text = Path(html_output).read_text(encoding="utf-8")
    checks["html_dashboard_title"] = "pass" if "VulnoraIQ Assessment Dashboard" in html_text else "fail"
    if checks["html_dashboard_title"] == "fail":
        errors.append("HTML dashboard title was not found.")

    status = "pass" if not errors else "fail"
    summary = FunctionalTestSummary(status, "demo", "baseline", str(output_root), str(screenshot_output), generated, checks, errors)
    summary_path.write_text(json.dumps(summary.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run VulnoraIQ functional acceptance test and generate dashboard example assets.")
    parser.add_argument("--output-dir", default="reports/output/functional-test")
    parser.add_argument("--screenshot", default="docs/assets/vulnoraiq-dashboard-example.svg")
    args = parser.parse_args()
    summary = run_functional_test(args.output_dir, args.screenshot)
    print(json.dumps(summary.to_dict(), indent=2, sort_keys=True))
    if summary.status != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
