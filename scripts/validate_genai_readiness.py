from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml

REQUIRED_GENAI_IDS = tuple(f"DSGAI{number:02d}" for number in range(1, 22))
SOURCE_DISCREPANCY_IDS = ("DSGAI22", "DSGAI23", "DSGAI24", "DSGAI25")
REQUIRED_FIXTURE_TYPES = {"secure", "vulnerable", "ambiguous", "edge_case"}
REQUIRED_SCENARIO_FIELDS = (
    "scenario_id",
    "genai_id",
    "risk_area",
    "fixture_type",
    "covered_fixture_types",
    "data_classification",
    "data_surface",
    "input_fixture",
    "expected_secure_outcome",
    "expected_vulnerable_signal",
    "required_evidence_fields",
    "mitre_atlas_tactics",
    "manual_review_required",
)
REQUIRED_EVIDENCE_FIELDS = {
    "genai_id",
    "genai_risk_area",
    "data_classification",
    "data_surface",
    "redaction_status",
    "manual_review_reason",
    "mitre_atlas_tactics",
}
ALLOWED_DATA_CLASSIFICATIONS = {"public", "internal", "confidential", "secret", "regulated"}
ALLOWED_DATA_SURFACES = {
    "prompt",
    "upload",
    "retrieval",
    "response",
    "tool_trace",
    "memory",
    "log",
    "report",
    "provider_metadata",
    "vector_store",
    "multimodal_input",
    "model_artifact",
}
MITRE_TACTIC_RE = re.compile(r"^AML\.TA\d{4}$")


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _validate_metadata(data: dict[str, Any], path: Path) -> list[str]:
    errors: list[str] = []
    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        return [f"{path}: missing metadata section"]
    if metadata.get("scope") != "controlled_internal_genai_security":
        errors.append(f"{path}: metadata.scope must be controlled_internal_genai_security")
    if metadata.get("source_confirmed_range") != "DSGAI01-DSGAI21":
        errors.append(f"{path}: metadata.source_confirmed_range must be DSGAI01-DSGAI21")
    discrepancy = metadata.get("source_discrepancy")
    if not isinstance(discrepancy, dict):
        errors.append(f"{path}: metadata.source_discrepancy must be tracked")
        return errors
    if discrepancy.get("status") != "tracked":
        errors.append(f"{path}: source discrepancy status must be tracked")
    unresolved = discrepancy.get("unresolved_ids")
    if not isinstance(unresolved, list) or sorted(unresolved) != sorted(SOURCE_DISCREPANCY_IDS):
        errors.append(f"{path}: source discrepancy must preserve DSGAI22-DSGAI25 as unresolved")
    return errors


def _validate_scenario(scenario: dict[str, Any], source: str) -> list[str]:
    errors: list[str] = []
    scenario_id = str(scenario.get("scenario_id", "<missing>"))
    prefix = f"{source}.{scenario_id}"

    for field in REQUIRED_SCENARIO_FIELDS:
        if scenario.get(field) in (None, "", []):
            errors.append(f"{prefix}: missing required field '{field}'")

    genai_id = scenario.get("genai_id")
    if genai_id not in REQUIRED_GENAI_IDS:
        errors.append(f"{prefix}: genai_id must be one of {list(REQUIRED_GENAI_IDS)}")

    fixture_type = scenario.get("fixture_type")
    if fixture_type not in REQUIRED_FIXTURE_TYPES:
        errors.append(f"{prefix}: invalid fixture_type '{fixture_type}'")

    covered_fixture_types = scenario.get("covered_fixture_types")
    if not isinstance(covered_fixture_types, list):
        errors.append(f"{prefix}: covered_fixture_types must be a list")
    else:
        invalid_fixture_types = sorted(set(covered_fixture_types) - REQUIRED_FIXTURE_TYPES)
        if invalid_fixture_types:
            errors.append(f"{prefix}: invalid covered_fixture_types {invalid_fixture_types}")

    data_classification = scenario.get("data_classification")
    if data_classification not in ALLOWED_DATA_CLASSIFICATIONS:
        errors.append(f"{prefix}: invalid data_classification '{data_classification}'")

    data_surface = scenario.get("data_surface")
    if data_surface not in ALLOWED_DATA_SURFACES:
        errors.append(f"{prefix}: invalid data_surface '{data_surface}'")

    evidence_fields = scenario.get("required_evidence_fields")
    if not isinstance(evidence_fields, list):
        errors.append(f"{prefix}: required_evidence_fields must be a list")
    else:
        missing_evidence = sorted(REQUIRED_EVIDENCE_FIELDS - set(evidence_fields))
        if missing_evidence:
            errors.append(f"{prefix}: missing required evidence fields {missing_evidence}")

    tactics = scenario.get("mitre_atlas_tactics")
    if not isinstance(tactics, list) or not tactics:
        errors.append(f"{prefix}: mitre_atlas_tactics must be a non-empty list")
    else:
        for tactic in tactics:
            if not isinstance(tactic, str) or not MITRE_TACTIC_RE.match(tactic):
                errors.append(f"{prefix}: invalid MITRE ATLAS tactic '{tactic}'")

    if "manual_review_required" in scenario and not isinstance(scenario.get("manual_review_required"), bool):
        errors.append(f"{prefix}: manual_review_required must be a boolean")

    return errors


def _scenario_fixture_types(scenario: dict[str, Any]) -> set[str]:
    fixture_types: set[str] = set()
    fixture_type = scenario.get("fixture_type")
    if isinstance(fixture_type, str):
        fixture_types.add(fixture_type)
    covered_fixture_types = scenario.get("covered_fixture_types")
    if isinstance(covered_fixture_types, list):
        fixture_types.update(str(item) for item in covered_fixture_types)
    return fixture_types


def validate_manifest(path: str | Path = "benchmarks/fixtures/genai/scenarios.yaml") -> dict[str, Any]:
    manifest_path = Path(path)
    if not manifest_path.exists():
        return {
            "status": "fail",
            "path": str(manifest_path),
            "scenario_count": 0,
            "errors": [f"{manifest_path}: file not found"],
        }

    data = _load_yaml(manifest_path)
    errors = _validate_metadata(data, manifest_path)
    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list):
        errors.append(f"{manifest_path}: scenarios must be a list")
        scenarios = []

    coverage: dict[str, set[str]] = {genai_id: set() for genai_id in REQUIRED_GENAI_IDS}
    seen_ids: set[str] = set()
    for raw_scenario in scenarios:
        if not isinstance(raw_scenario, dict):
            errors.append(f"{manifest_path}: scenario entry must be a mapping")
            continue
        scenario_id = str(raw_scenario.get("scenario_id", ""))
        if scenario_id in seen_ids:
            errors.append(f"{manifest_path}.{scenario_id}: duplicate scenario_id")
        seen_ids.add(scenario_id)
        genai_id = raw_scenario.get("genai_id")
        if genai_id in coverage:
            coverage[str(genai_id)].update(_scenario_fixture_types(raw_scenario))
        errors.extend(_validate_scenario(raw_scenario, str(manifest_path)))

    for genai_id, fixture_types in coverage.items():
        missing = sorted(REQUIRED_FIXTURE_TYPES - fixture_types)
        if missing:
            errors.append(f"{manifest_path}.{genai_id}: missing fixture types {missing}")

    return {
        "status": "fail" if errors else "pass",
        "path": str(manifest_path),
        "scenario_count": len(scenarios),
        "expected_genai_ids": list(REQUIRED_GENAI_IDS),
        "required_fixture_types": sorted(REQUIRED_FIXTURE_TYPES),
        "errors": errors,
    }


def validate_docs(
    plan_path: str | Path = "docs/genai/PRODUCTION_READINESS_PLAN.md",
    readme_path: str | Path = "docs/genai/README.md",
) -> dict[str, Any]:
    errors: list[str] = []
    plan = Path(plan_path)
    readme = Path(readme_path)
    if not plan.exists():
        errors.append(f"{plan}: file not found")
    else:
        plan_text = plan.read_text(encoding="utf-8")
        for required_text in (
            "Plan status: Completed",
            "controlled internal enterprise deployment",
            "DSGAI01–DSGAI21",
            "Phase GENAI-6",
            "public internet / SaaS hardening remains deferred",
        ):
            if required_text not in plan_text:
                errors.append(f"{plan}: missing required text '{required_text}'")
    if not readme.exists():
        errors.append(f"{readme}: file not found")
    else:
        readme_text = readme.read_text(encoding="utf-8")
        for required_text in (
            "Working starter",
            "benchmarks/fixtures/genai/scenarios.yaml",
            "scripts/validate_genai_readiness.py",
        ):
            if required_text not in readme_text:
                errors.append(f"{readme}: missing required text '{required_text}'")
    return {"status": "fail" if errors else "pass", "errors": errors}


def validate_default() -> dict[str, Any]:
    manifest_result = validate_manifest()
    docs_result = validate_docs()
    errors = [*manifest_result["errors"], *docs_result["errors"]]
    return {
        "status": "fail" if errors else "pass",
        "manifest": manifest_result,
        "docs": docs_result,
        "errors": errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate GenAI Security production-readiness scenario manifests and docs.")
    parser.add_argument("--manifest", default="benchmarks/fixtures/genai/scenarios.yaml")
    parser.add_argument("--plan", default="docs/genai/PRODUCTION_READINESS_PLAN.md")
    parser.add_argument("--readme", default="docs/genai/README.md")
    args = parser.parse_args()

    manifest_result = validate_manifest(args.manifest)
    docs_result = validate_docs(args.plan, args.readme)
    errors = [*manifest_result["errors"], *docs_result["errors"]]
    result = {"status": "fail" if errors else "pass", "manifest": manifest_result, "docs": docs_result, "errors": errors}
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
