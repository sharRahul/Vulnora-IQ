from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml

REQUIRED_MAPPING_FIELDS = (
    "owasp_family",
    "owasp_id",
    "mitre_atlas_tactics",
    "mapping_status",
    "evidence_surface",
    "manual_review_required",
)

ALLOWED_OWASP_FAMILIES = {"LLM", "GenAI Data", "Agentic"}
ALLOWED_MAPPING_STATUSES = {"candidate", "validated", "rejected", "map_later"}
ALLOWED_EVIDENCE_SURFACES = {
    "audit_log",
    "config_metadata",
    "context_window",
    "memory_trace",
    "model_metadata",
    "output_artifact",
    "policy_metadata",
    "prompt",
    "provider_metadata",
    "report_artifact",
    "request_trace",
    "response",
    "retrieval_trace",
    "scanner_evidence",
    "telemetry",
    "tool_trace",
    "vector_store",
}
MITRE_TACTIC_RE = re.compile(r"^AML\.TA\d{4}$")


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _is_active(entry: dict[str, Any]) -> bool:
    return entry.get("active", True) is not False and entry.get("enabled", True) is not False


def _validate_owasp_id(entry_id: str, family: str, owasp_id: str) -> list[str]:
    errors: list[str] = []
    if family == "LLM" and not re.match(r"^LLM\d{2}:2025$", owasp_id):
        errors.append(f"{entry_id}: LLM mapping has invalid owasp_id '{owasp_id}'")
    if family == "GenAI Data" and not re.match(r"^DSGAI\d{2}$", owasp_id):
        errors.append(f"{entry_id}: GenAI Data mapping has invalid owasp_id '{owasp_id}'")
    if family == "Agentic" and not re.match(r"^ASI\d{2}$", owasp_id):
        errors.append(f"{entry_id}: Agentic mapping has invalid owasp_id '{owasp_id}'")
    return errors


def _validate_entry(source_name: str, entry_id: str, entry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    prefix = f"{source_name}.{entry_id}"

    for field in REQUIRED_MAPPING_FIELDS:
        if field not in entry or entry[field] in (None, "", []):
            errors.append(f"{prefix}: missing required mapping field '{field}'")

    family = str(entry.get("owasp_family", ""))
    if family and family not in ALLOWED_OWASP_FAMILIES:
        errors.append(
            f"{prefix}: invalid owasp_family '{family}', expected one of {sorted(ALLOWED_OWASP_FAMILIES)}"
        )

    owasp_id = str(entry.get("owasp_id", ""))
    if family and owasp_id:
        errors.extend(_validate_owasp_id(prefix, family, owasp_id))

    tactics = entry.get("mitre_atlas_tactics")
    if tactics is not None:
        if not isinstance(tactics, list) or not tactics:
            errors.append(f"{prefix}: mitre_atlas_tactics must be a non-empty list")
        else:
            for tactic in tactics:
                if not isinstance(tactic, str) or not MITRE_TACTIC_RE.match(tactic):
                    errors.append(f"{prefix}: invalid MITRE ATLAS tactic '{tactic}'")

    mapping_status = entry.get("mapping_status")
    if mapping_status is not None and mapping_status not in ALLOWED_MAPPING_STATUSES:
        errors.append(
            f"{prefix}: invalid mapping_status '{mapping_status}', expected one of {sorted(ALLOWED_MAPPING_STATUSES)}"
        )

    evidence_surface = entry.get("evidence_surface")
    if evidence_surface is not None:
        if not isinstance(evidence_surface, list) or not evidence_surface:
            errors.append(f"{prefix}: evidence_surface must be a non-empty list")
        else:
            for surface in evidence_surface:
                if not isinstance(surface, str) or surface not in ALLOWED_EVIDENCE_SURFACES:
                    errors.append(f"{prefix}: invalid evidence_surface '{surface}'")

    if "manual_review_required" in entry and not isinstance(entry.get("manual_review_required"), bool):
        errors.append(f"{prefix}: manual_review_required must be a boolean")

    return errors


def validate_mapping_file(path: str | Path, section_name: str, source_name: str | None = None) -> dict[str, Any]:
    file_path = Path(path)
    source = source_name or str(file_path)
    errors: list[str] = []

    if not file_path.exists():
        return {
            "path": str(file_path),
            "section": section_name,
            "status": "fail",
            "checked_count": 0,
            "skipped_count": 0,
            "errors": [f"{file_path}: file not found"],
        }

    data = _load_yaml(file_path)
    section = data.get(section_name)
    if not isinstance(section, dict):
        return {
            "path": str(file_path),
            "section": section_name,
            "status": "fail",
            "checked_count": 0,
            "skipped_count": 0,
            "errors": [f"{file_path}: missing or invalid '{section_name}' section"],
        }

    checked_count = 0
    skipped_count = 0
    for entry_id, raw_entry in section.items():
        if not isinstance(raw_entry, dict):
            errors.append(f"{source}.{entry_id}: entry must be a mapping")
            continue
        if not _is_active(raw_entry):
            skipped_count += 1
            continue
        checked_count += 1
        errors.extend(_validate_entry(source, str(entry_id), raw_entry))

    if checked_count == 0:
        errors.append(f"{source}: no active entries found in '{section_name}'")

    return {
        "path": str(file_path),
        "section": section_name,
        "status": "fail" if errors else "pass",
        "checked_count": checked_count,
        "skipped_count": skipped_count,
        "errors": errors,
    }


def validate_default_configs(
    oracles_path: str | Path = "config/owasp_oracles.yaml",
    production_detection_path: str | Path = "config/production_owasp_detection.yaml",
) -> dict[str, Any]:
    results = [
        validate_mapping_file(oracles_path, "oracles", "owasp_oracles"),
        validate_mapping_file(production_detection_path, "rules", "production_owasp_detection"),
    ]
    errors = [error for result in results for error in result["errors"]]
    return {
        "status": "fail" if errors else "pass",
        "checked_count": sum(int(result["checked_count"]) for result in results),
        "skipped_count": sum(int(result["skipped_count"]) for result in results),
        "results": results,
        "errors": errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate OWASP-to-MITRE ATLAS mapping metadata for active VulnoraIQ oracles/checks."
    )
    parser.add_argument("--oracles", default="config/owasp_oracles.yaml")
    parser.add_argument("--production-detection", default="config/production_owasp_detection.yaml")
    args = parser.parse_args()

    result = validate_default_configs(args.oracles, args.production_detection)
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
