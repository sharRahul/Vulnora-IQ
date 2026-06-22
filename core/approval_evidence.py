from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import yaml


@dataclass(slots=True)
class ApprovalValidationResult:
    approval_id: str
    status: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class ApprovalEvidenceRegistry:
    """Validates local approval evidence references used by policy exceptions."""

    def __init__(self, path: str | Path = "config/approval_evidence.yaml") -> None:
        self.path = Path(path)

    def validate_reference(self, approval_id: str | None) -> ApprovalValidationResult:
        if not approval_id:
            return ApprovalValidationResult("", "fail", ["Approval reference is missing"])
        if not self.path.exists():
            return ApprovalValidationResult(str(approval_id), "fail", [f"Approval evidence register not found: {self.path}"])
        data = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
        approvals = {str(item.get("id")): item for item in data.get("approvals", [])}
        approval = approvals.get(str(approval_id))
        if not approval:
            return ApprovalValidationResult(str(approval_id), "fail", [f"Approval reference not found: {approval_id}"])
        errors = self._validate_approval(approval)
        return ApprovalValidationResult(str(approval_id), "fail" if errors else "pass", errors)

    @staticmethod
    def expected_signature(canonical_statement: str) -> str:
        return hashlib.sha256(canonical_statement.encode("utf-8")).hexdigest()

    def _validate_approval(self, approval: dict[str, Any]) -> list[str]:
        required = {"id", "owner", "approver", "scope", "issued_on", "expires_on", "canonical_statement", "signature_algorithm", "signature"}
        errors: list[str] = []
        missing = sorted(required - set(approval))
        if missing:
            return [f"Approval is missing fields: {', '.join(missing)}"]
        if str(approval["signature_algorithm"]).lower() != "sha256":
            errors.append("Unsupported signature_algorithm; expected sha256")
        if date.fromisoformat(str(approval["expires_on"])) < date.today():
            errors.append("Approval evidence is expired")
        expected = self.expected_signature(str(approval["canonical_statement"]))
        if str(approval["signature"]) != expected:
            errors.append("Approval signature does not match canonical_statement")
        return errors
