from __future__ import annotations

from core.production_detection import ProductionOwaspDetector
from core.scanner import Scanner


def test_production_detector_config_covers_all_owasp_categories():
    result = ProductionOwaspDetector().validate_config()

    assert result.status == "pass"
    assert len(result.covered_modules) == 10
    assert result.missing_modules == []


def test_production_detector_classifies_control_and_failure_signals():
    detector = ProductionOwaspDetector()
    evidence = {
        "payload_id": "unit",
        "response_preview": "control observed",
        "target": "unit",
        "prompt_category": "sensitive_information",
        "owasp_id": "LLM02:2025",
    }

    passing = detector.evaluate(
        "owasp_llm02_sensitive_information_disclosure",
        evidence,
        "Sensitive data refused. Redaction applied and high-level explanation only.",
    )
    failing = detector.evaluate(
        "owasp_llm02_sensitive_information_disclosure",
        evidence,
        "Credential exposed during the response.",
    )

    assert passing.status == "pass"
    assert passing.verdict == "control_observed" or passing.matched_pass_signals
    assert failing.status == "fail"
    assert failing.risk_score >= 9.0
    assert failing.matched_fail_signals


def test_demo_full_profile_has_production_detection_evidence():
    result = Scanner().scan(target_name="demo", profile_name="full")

    assert result.metadata["production_validation_status"] == "authorised_production_assessment_testing_ready"
    assert result.metadata["production_owasp_detection"]["covered_category_count"] == 10
    assert result.finding_count >= 10
    for finding in result.findings:
        summary = finding.evidence.get("production_detection_status_summary", {})
        assert "production_detection_profile" in finding.evidence
        assert int(summary.get("fail", 0)) == 0
