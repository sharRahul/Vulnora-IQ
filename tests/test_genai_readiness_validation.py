from __future__ import annotations

from pathlib import Path

import yaml

from core.genai_evaluators import GenAIDataSecurityEvaluatorSuite, GenAIEvaluatorResult
from scripts.validate_genai_readiness import REQUIRED_CASE_COUNT, validate_default, validate_manifest


def _write_yaml(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


REQUIRED_EVIDENCE_FIELDS = [
    "genai_id",
    "genai_risk_area",
    "scenario_id",
    "fixture_type",
    "data_classification",
    "data_surface",
    "control_objective",
    "production_signal",
    "redaction_status",
    "manual_review_reason",
    "evaluator_chain",
    "acceptance_criteria",
    "severity",
    "confidence_floor",
    "mitre_atlas_tactics",
    "false_positive_notes",
    "false_negative_notes",
]


def _valid_manifest() -> dict:
    return {
        "metadata": {
            "version": 2,
            "scope": "controlled_internal_genai_security",
            "status": "production_scenario_harness_complete",
            "scenario_harness_maturity": "production_grade_controlled_internal",
            "assurance_boundary": "production-grade scenario harness for controlled internal validation; not independent real-world detection assurance",
            "source_confirmed_range": "DSGAI01-DSGAI21",
            "source_discrepancy": {
                "status": "tracked",
                "referenced_range": "DSGAI01-DSGAI25",
                "confirmed_range": "DSGAI01-DSGAI21",
                "unresolved_ids": ["DSGAI22", "DSGAI23", "DSGAI24", "DSGAI25"],
            },
            "review_gate": {
                "ci_required": True,
                "human_review_required": True,
                "external_assurance_required_for_public_claims": True,
                "last_updated": "2026-06-23",
            },
        },
        "scenario_matrix": {
            "expansion": "categories_x_fixture_cases",
            "case_id_format": "{genai_id}-{case_suffix}",
            "expected_case_count": REQUIRED_CASE_COUNT,
            "required_fixture_types": ["secure", "vulnerable", "ambiguous", "edge_case"],
        },
        "evidence_contract": {
            "version": "genai-production-v2",
            "required_evidence_fields": REQUIRED_EVIDENCE_FIELDS,
            "evaluator_chain": [
                "data_classification_present",
                "data_surface_allowed",
                "evidence_fields_present",
                "restricted_marker_leakage",
                "scenario_expectation",
                "confidence_floor_met",
                "acceptance_criteria_present",
            ],
            "acceptance_criteria": [
                "required evidence fields present",
                "safe synthetic fixture only",
                "result matches fixture expectation",
                "manual review reason recorded",
            ],
            "false_positive_notes": "Manual review confirms context.",
            "false_negative_notes": "Authorised environment validation remains required.",
        },
        "fixture_cases": [
            {
                "fixture_type": "secure",
                "case_suffix": "secure-baseline",
                "data_classification": "confidential",
                "severity": "medium",
                "confidence_floor": 0.88,
                "production_signal": "controls present",
                "manual_review_required": True,
                "safe_fixture": True,
                "production_grade": True,
                "real_world_validation_required": True,
            },
            {
                "fixture_type": "vulnerable",
                "case_suffix": "vulnerable-control-gap",
                "data_classification": "regulated",
                "severity": "high",
                "confidence_floor": 0.88,
                "production_signal": "controlled gap detected",
                "manual_review_required": True,
                "safe_fixture": True,
                "production_grade": True,
                "real_world_validation_required": True,
            },
            {
                "fixture_type": "ambiguous",
                "case_suffix": "ambiguous-review",
                "data_classification": "internal",
                "severity": "medium",
                "confidence_floor": 0.82,
                "production_signal": "mixed evidence routed to review",
                "manual_review_required": True,
                "safe_fixture": True,
                "production_grade": True,
                "real_world_validation_required": True,
            },
            {
                "fixture_type": "edge_case",
                "case_suffix": "edge-case-boundary",
                "data_classification": "secret",
                "severity": "high",
                "confidence_floor": 0.82,
                "production_signal": "boundary case routed to review",
                "manual_review_required": True,
                "safe_fixture": True,
                "production_grade": True,
                "real_world_validation_required": True,
            },
        ],
        "categories": [
            {
                "genai_id": f"DSGAI{number:02d}",
                "risk_area": "Sensitive Data Leakage",
                "data_surface": "prompt",
                "mitre_atlas_tactics": ["AML.TA0002"],
                "control_objective": "Validate controls using safe synthetic evidence.",
            }
            for number in range(1, 22)
        ],
    }


def test_validate_default_genai_readiness_passes_repository_files() -> None:
    result = validate_default()

    assert result["status"] == "pass"
    assert result["manifest"]["scenario_count"] == REQUIRED_CASE_COUNT
    assert result["errors"] == []


def test_validate_manifest_requires_all_source_confirmed_categories(tmp_path: Path) -> None:
    path = tmp_path / "scenarios.yaml"
    manifest = _valid_manifest()
    manifest["categories"] = manifest["categories"][:-1]
    _write_yaml(path, manifest)

    result = validate_manifest(path)

    assert result["status"] == "fail"
    assert any("categories missing" in error or "expanded scenario matrix" in error for error in result["errors"])


def test_validate_manifest_rejects_incomplete_fixture_matrix(tmp_path: Path) -> None:
    path = tmp_path / "scenarios.yaml"
    manifest = _valid_manifest()
    manifest["fixture_cases"] = manifest["fixture_cases"][:-1]
    _write_yaml(path, manifest)

    result = validate_manifest(path)

    assert result["status"] == "fail"
    assert any("fixture_cases missing" in error or "expanded scenario matrix" in error for error in result["errors"])


def test_validate_manifest_rejects_missing_production_fields(tmp_path: Path) -> None:
    path = tmp_path / "scenarios.yaml"
    manifest = _valid_manifest()
    del manifest["fixture_cases"][0]["production_grade"]
    manifest["fixture_cases"][1]["confidence_floor"] = 0.5
    _write_yaml(path, manifest)

    result = validate_manifest(path)

    assert result["status"] == "fail"
    assert any("production_grade" in error for error in result["errors"])
    assert any("confidence_floor" in error for error in result["errors"])


def test_validate_manifest_rejects_missing_evidence_and_bad_tactic(tmp_path: Path) -> None:
    path = tmp_path / "scenarios.yaml"
    manifest = _valid_manifest()
    manifest["evidence_contract"]["required_evidence_fields"] = ["genai_id"]
    manifest["categories"][0]["mitre_atlas_tactics"] = ["TA0002"]
    _write_yaml(path, manifest)

    result = validate_manifest(path)

    assert result["status"] == "fail"
    assert any("required_evidence_fields missing" in error for error in result["errors"])
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


def test_confidence_floor_and_aggregate_result() -> None:
    passing = GenAIDataSecurityEvaluatorSuite.confidence_floor_met(0.91, 0.88)
    failing = GenAIDataSecurityEvaluatorSuite.confidence_floor_met(0.7, 0.88)
    aggregate = GenAIDataSecurityEvaluatorSuite.aggregate_results(
        [
            passing,
            GenAIEvaluatorResult("synthetic_warning", "warn", 0.9, "review"),
        ],
        confidence_floor=0.88,
    )

    assert passing.status == "pass"
    assert failing.status == "fail"
    assert aggregate.status == "warn"
    assert aggregate.manual_review_required is True
