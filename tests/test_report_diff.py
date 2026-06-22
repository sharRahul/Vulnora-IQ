from __future__ import annotations

import json

from reports.report_diff import diff_reports, write_markdown


def write_report(path, *, policy_status="pass", findings=None, severity_counts=None):
    payload = {
        "target": "demo",
        "profile": "baseline",
        "finding_count": len(findings or []),
        "policy_status": policy_status,
        "severity_counts": severity_counts or {},
        "findings": findings or [],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_report_diff_detects_added_finding(tmp_path) -> None:
    baseline = tmp_path / "baseline.json"
    current = tmp_path / "current.json"
    write_report(baseline, findings=[], severity_counts={"info": 0})
    write_report(
        current,
        findings=[
            {
                "title": "New finding",
                "severity": "medium",
                "score": 4.0,
                "owasp_id": "LLM01:2025",
                "affected_component": "Prompt layer",
                "recommendation": "Review control.",
                "mitre_atlas": ["AML.T0051"],
            }
        ],
        severity_counts={"medium": 1},
    )

    diff = diff_reports(baseline, current)

    assert diff.finding_count_delta == 1
    assert diff.added_findings[0]["title"] == "New finding"
    assert diff.has_regression is True


def test_report_diff_detects_policy_status_change(tmp_path) -> None:
    baseline = tmp_path / "baseline.json"
    current = tmp_path / "current.json"
    write_report(baseline, policy_status="pass")
    write_report(current, policy_status="fail")

    diff = diff_reports(baseline, current)

    assert diff.policy_status_changed is True
    assert diff.has_regression is True


def test_report_diff_writes_markdown(tmp_path) -> None:
    baseline = tmp_path / "baseline.json"
    current = tmp_path / "current.json"
    markdown = tmp_path / "diff.md"
    write_report(baseline)
    write_report(current)

    output = write_markdown(diff_reports(baseline, current), markdown)

    assert "LLM Assessment Report Diff" in output.read_text(encoding="utf-8")
