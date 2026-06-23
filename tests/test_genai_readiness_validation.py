from __future__ import annotations

from pathlib import Path

import yaml

from core.genai_evaluators import GenAIDataSecurityEvaluatorSuite
from scripts.validate_genai_readiness import validate_default, validate_manifest


def _write_yaml(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _valid_scenario(genai_id: str = "DSGAI01") -> dict:
    return {
        "scenario_id": f"{genai_id}-coverage-suite",
        "genai_id": genai_id,
        "risk_area": "Sensitive Data Leakage",
        "fixture_type": "secure",
        "covered_fixture_types": ["secure", "vulnerable", "ambiguous", "edge_case"],
        "data_classification": "internal",
        "data_surface": "prompt",
        "input_fixture": "Safe synthetic GenAI fixture suite.",
        "expected_secure_outcome": "No restricted marker appears outside approved evidence fields.",
        "expected_vulnerable_signal": "Synthetic restricted marker appears outside approved evidence fields.",
        "required_evidence_fields": [
            "genai_id",
            "genai_risk_area",
            "data_classification",
            "data_surface",
            "redaction_status",
            "manual_review_reason",
            "mitre_atlas_tactics",
        ],
        "mitre_atlas_tactics": ["AML.TA0002"],
        "manual_review_required": True,
    }


def _valid_manifest() -> dict:
    return {
        "metadata": {
            "version": 1,
            "scope": "controlled_internal_genai_security",
            "status": "working_starter_gate_complete",
            "source_confirmed_range": "DSGAI01-DSGAI21",
            "source_discrepancy": {
                "status": "tracked",
                "referenced_range": "DSGAI01-DSGAI25",
                "confirmed_range": "DSGAI01-DSGAI21",
                "unresolved_ids": ["DSGAI22", "DSGAI23", "DSGAI24", "DSGAI25"],
            },
        },
        "scenarios": [_valid_scenario(f"DSGAI{number:02d}") for number in range(1, 22)],
    }


def test_validate_default_genai_readiness_passes_repository_files() -> None:
    result = validate_default()

    assert result["status"] == "pass"
    assert result["manifest"]["scenario_count"] >= 21
    assert result["errors"] == []


def test_validate_manifest_requires_all_dsgai_fixture_types(tmp_path: Path) -> None:
    path = tmp_path / "scenarios.yaml"
    manifest = _valid_manifest()
    manifest["scenarios"][0]["covered_fixture_types"] = ["secure", "vulnerable"]
    _write_yaml(path, manifest)

    result = validate_manifest(path)

    assert result["status"] == "fail"
    assert any("missing fixture types" in error for error in result["errors"])


def test_validate_manifest_rejects_missing_evidence_and_bad_tactic(tmp_path: Path) -> None:
    path = tmp_path / "scenarios.yaml"
    manifest = _valid_manifest()
    manifest["scenarios"][0]["required_evidence_fields"] = ["genai_id"]
    manifest["scenarios"][0]["mitre_atlas_tactics"] = ["TA0002"]
    _write_yaml(path, manifest)

    result = validate_manifest(path)

    assert result["status"] == "fail"
    assert any("missing required evidence fields" in error for error in result["errors"])
    assert any("invalid MITRE ATLAS tactic" in error for error in result["errors"])


def test_restricted_marker_evaluator_detects_synthetic_leakage() -> None:
    result = GenAIDataSecurityEvaluatorSuite.restricted_marker_leakage("leaked SYNTHETIC_SECRET_TEST_VALUE")

    assert result.status == "fail"
    assert result.manual_review_required is True
    assert result.evidence_fields["matches"] == ["SYNTHETIC_SECRET_TEST_VALUE"]


def test_restricted_marker_evaluator_allows_approved_evidence_context() -> None:
    result = GenAIDataSecurityEvaluatorSuite.restricted_marker_leakage(
        "controlled evidence SYNTHETIC_SECRET_TEST_VALUE",
        allowed_context=True,
    )

    assert result.status == "pass"
    assert result.manual_review_required is False


def test_evidence_field_evaluator_reports_missing_fields() -> None:
    result = GenAIDataSecurityEvaluatorSuite.evidence_fields_present(
        {"genai_id": "DSGAI01"},
        ["genai_id", "data_surface"],
    )

    assert result.status == "fail"
    assert result.evidence_fields["missing"] == ["data_surface"]
