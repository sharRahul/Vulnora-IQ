from __future__ import annotations

from core.mitre_atlas import MitreAtlasMapping
from core.scanner import Scanner


def test_mitre_atlas_mapping_catalog_validates() -> None:
    result = MitreAtlasMapping().validate()

    assert result.status == "pass"
    assert result.technique_count >= 20
    assert result.module_mapping_count >= 10
    assert not result.errors


def test_starter_findings_use_validated_atlas_mapping() -> None:
    result = Scanner().scan(target_name="demo", profile_name="baseline")

    prompt_finding = next(finding for finding in result.findings if finding.owasp_id == "LLM01:2025")
    assert "AML.T0051" in prompt_finding.mitre_atlas
    assert prompt_finding.evidence["mitre_atlas_validated"] is True
    assert all(item.startswith("AML.T") for item in prompt_finding.mitre_atlas)
