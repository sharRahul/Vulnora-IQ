from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


HASH_RE = re.compile(r"^[a-fA-F0-9]{64}$")
REQUIRED_DOCUMENT_FIELDS = {
    "id",
    "title",
    "source_uri",
    "owner",
    "classification",
    "approval_status",
    "content_hash",
    "last_reviewed",
    "allowed_groups",
}


@dataclass(slots=True)
class CorpusValidationResult:
    manifest_path: str
    document_count: int
    status: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class CorpusManifestValidator:
    """Validates RAG corpus manifest metadata before retrieval testing."""

    def validate(self, manifest_path: str | Path) -> CorpusValidationResult:
        path = Path(manifest_path)
        if not path.exists():
            return CorpusValidationResult(
                manifest_path=str(path),
                document_count=0,
                status="fail",
                errors=[f"Manifest file not found: {path}"],
            )

        manifest = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        documents = manifest.get("documents", [])
        errors: list[str] = []
        warnings: list[str] = []

        if not manifest.get("name"):
            errors.append("Manifest is missing name")
        if not manifest.get("version"):
            errors.append("Manifest is missing version")
        if manifest.get("hash_algorithm") != "sha256":
            warnings.append("Manifest hash_algorithm should be sha256")
        if manifest.get("approval_required") is not True:
            warnings.append("Manifest approval_required should be true")
        if not isinstance(documents, list) or not documents:
            errors.append("Manifest must contain at least one document")
            documents = []

        seen_ids: set[str] = set()
        for index, document in enumerate(documents, start=1):
            errors.extend(self._validate_document(index, document, seen_ids))

        status = "fail" if errors else "warn" if warnings else "pass"
        return CorpusValidationResult(
            manifest_path=str(path),
            document_count=len(documents),
            status=status,
            errors=errors,
            warnings=warnings,
        )

    def _validate_document(self, index: int, document: dict[str, Any], seen_ids: set[str]) -> list[str]:
        errors: list[str] = []
        missing = sorted(REQUIRED_DOCUMENT_FIELDS - set(document))
        if missing:
            errors.append(f"Document {index} is missing fields: {', '.join(missing)}")
            return errors

        doc_id = str(document["id"])
        if doc_id in seen_ids:
            errors.append(f"Duplicate document id: {doc_id}")
        seen_ids.add(doc_id)

        if str(document["approval_status"]).lower() != "approved":
            errors.append(f"Document {doc_id} is not approved")
        if not HASH_RE.match(str(document["content_hash"])):
            errors.append(f"Document {doc_id} has invalid sha256 content_hash")
        if not isinstance(document.get("allowed_groups"), list) or not document["allowed_groups"]:
            errors.append(f"Document {doc_id} must define at least one allowed group")
        return errors
