from __future__ import annotations

import json

from core.scanner import Scanner
from dashboards.html_dashboard import HtmlDashboardGenerator
from reports.json_report_generator import JsonReportGenerator
from reports.sarif_report_generator import SarifReportGenerator


def test_sarif_report_contains_results(tmp_path) -> None:
    result = Scanner().scan(target_name="demo", profile_name="baseline")
    output = SarifReportGenerator().generate(result, tmp_path / "report.sarif")

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["version"] == "2.1.0"
    assert data["runs"][0]["tool"]["driver"]["name"] == "VulnoraIQ"
    assert data["runs"][0]["results"]
    assert data["runs"][0]["tool"]["driver"]["rules"]


def test_html_dashboard_contains_summary(tmp_path) -> None:
    result = Scanner().scan(target_name="demo", profile_name="baseline")
    json_output = JsonReportGenerator().generate(result, tmp_path / "report.json")
    report = json.loads(json_output.read_text(encoding="utf-8"))
    output = HtmlDashboardGenerator().generate_from_report(report, tmp_path / "dashboard.html")

    html = output.read_text(encoding="utf-8")
    assert "VulnoraIQ Assessment Dashboard" in html
    assert "Policy evaluation" in html
    assert "Raw structured report" in html
