from __future__ import annotations

from integrations.contract_validation import TargetContractValidator


def test_default_target_contracts_allow_empty_real_target_config() -> None:
    result = TargetContractValidator().validate()

    assert result.status == "pass"
    assert result.target_count == 0
    assert result.validated_count == 0
    assert not result.errors
    assert not result.warnings
