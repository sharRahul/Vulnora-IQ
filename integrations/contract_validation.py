from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(slots=True)
class TargetContractValidationResult:
    status: str
    target_count: int
    validated_count: int
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class TargetContractValidator:
    """Validates configured target adapter shapes before authorised testing."""

    def __init__(
        self,
        targets_path: str | Path = "config/targets.yaml",
        contracts_path: str | Path = "config/target_contracts.yaml",
    ) -> None:
        self.targets_path = Path(targets_path)
        self.contracts_path = Path(contracts_path)

    def validate(self) -> TargetContractValidationResult:
        targets = yaml.safe_load(self.targets_path.read_text(encoding="utf-8")) or {}
        contracts = yaml.safe_load(self.contracts_path.read_text(encoding="utf-8")) or {}
        errors: list[str] = []
        warnings: list[str] = []
        validated = 0
        configured = targets.get("targets", {})
        for name, target in configured.items():
            contract_name = self._contract_for_type(str(target.get("type")), contracts.get("contracts", {}))
            if not contract_name:
                errors.append(f"Target {name} uses unsupported type {target.get('type')}")
                continue
            contract = contracts["contracts"][contract_name]
            for field_name in contract.get("required_fields", []):
                if not target.get(field_name):
                    errors.append(f"Target {name} missing required field {field_name}")
            endpoint = str(target.get("endpoint", ""))
            if "example.invalid" in endpoint or not endpoint:
                warnings.append(f"Target {name} is still a placeholder and cannot be used for real assessment.")
            validated += 1
        status = "fail" if errors else "warn" if warnings else "pass"
        return TargetContractValidationResult(status, len(configured), validated, errors, warnings)

    @staticmethod
    def _contract_for_type(target_type: str, contracts: dict[str, Any]) -> str | None:
        for contract_name, contract in contracts.items():
            if target_type in contract.get("allowed_types", []):
                return str(contract_name)
        return None
