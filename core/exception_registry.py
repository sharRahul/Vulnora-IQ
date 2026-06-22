from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from core.types import PolicyResult, ScanResult


@dataclass(frozen=True, slots=True)
class PolicyException:
    id: str
    policy_id: str
    status: str
    owner: str
    reason: str
    expires_on: date
    target: str | None = None
    profile: str | None = None
    finding_title: str | None = None
    approval_reference: str | None = None
    compensating_controls: list[str] | None = None

    @property
    def is_active(self) -> bool:
        return self.status.lower() == "active" and self.expires_on >= date.today()


class PolicyExceptionRegistry:
    """Loads and applies scoped policy exceptions."""

    def __init__(self, path: str | Path = "config/policy_exceptions.yaml") -> None:
        self.path = Path(path)

    def load(self) -> list[PolicyException]:
        if not self.path.exists():
            return []
        raw = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
        exceptions = raw.get("exceptions", []) or []
        return [self._parse(item) for item in exceptions]

    def apply(self, result: ScanResult, policy_results: list[PolicyResult]) -> list[PolicyResult]:
        exceptions = self.load()
        updated: list[PolicyResult] = []
        for policy_result in policy_results:
            matching = [exc for exc in exceptions if self._matches(exc, result, policy_result)]
            if matching and policy_result.status in {"fail", "warn"}:
                active = [exc for exc in matching if exc.is_active]
                if active:
                    ids = [exc.id for exc in active]
                    updated.append(
                        PolicyResult(
                            policy_id=policy_result.policy_id,
                            status="warn",
                            decision=policy_result.decision,
                            message=f"Policy result suppressed by active exception(s): {', '.join(ids)}.",
                            evidence={
                                **policy_result.evidence,
                                "original_status": policy_result.status,
                                "active_exceptions": ids,
                            },
                        )
                    )
                    continue
            updated.append(policy_result)
        return updated

    @staticmethod
    def _matches(exception: PolicyException, result: ScanResult, policy_result: PolicyResult) -> bool:
        if exception.policy_id != policy_result.policy_id:
            return False
        if exception.target and exception.target != result.target_name:
            return False
        if exception.profile and exception.profile != result.profile_name:
            return False
        return True

    @staticmethod
    def _parse(item: dict[str, Any]) -> PolicyException:
        return PolicyException(
            id=str(item["id"]),
            policy_id=str(item["policy_id"]),
            status=str(item["status"]),
            owner=str(item["owner"]),
            reason=str(item["reason"]),
            expires_on=date.fromisoformat(str(item["expires_on"])),
            target=item.get("target"),
            profile=item.get("profile"),
            finding_title=item.get("finding_title"),
            approval_reference=item.get("approval_reference"),
            compensating_controls=list(item.get("compensating_controls", [])),
        )
