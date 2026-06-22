from __future__ import annotations

from pathlib import Path

import yaml

from core.payload_loader import PayloadLibrary

SOURCE_DIRECTORY = "docs/owasp-documents/"

REQUIRED_GENAI_FAMILIES = {
    "genai_governance",
    "genai_context_boundary",
    "genai_retrieval_trust",
    "genai_agent_approval",
    "genai_output_validation",
    "genai_generated_content_review",
    "genai_provenance_audit",
    "genai_resource_boundary",
}

REQUIRED_PRIVACY_FAMILIES = {
    "privacy_minimisation",
    "privacy_consent_lawful_basis",
    "privacy_purpose_limitation",
    "privacy_redaction",
    "privacy_tenant_boundary",
    "privacy_retention_deletion",
    "privacy_audit_logging",
    "privacy_processor_review",
    "privacy_impact_review",
    "privacy_user_rights",
}


def _payload_data() -> dict:
    return yaml.safe_load(Path("payloads/owasp_genai_data_privacy.yaml").read_text(encoding="utf-8"))


def _families() -> set[str]:
    return {payload["metadata"]["scenario_family"] for payload in _payload_data()["payloads"]}


def test_genai_and_privacy_families_are_complete():
    families = _families()
    assert REQUIRED_GENAI_FAMILIES <= families
    assert REQUIRED_PRIVACY_FAMILIES <= families


def test_genai_data_privacy_payload_metadata_is_complete():
    data = _payload_data()
    assert data["source"]["source_directory"] == SOURCE_DIRECTORY
    for payload in data["payloads"]:
        metadata = payload["metadata"]
        assert payload["id"]
        assert payload["input"]
        assert payload["expected_behavior"]
        assert metadata["source_directory"] == SOURCE_DIRECTORY
        assert metadata["scenario_family"]
        assert metadata["control_objective"]
        assert metadata["review_status"] == "reviewed"
        assert metadata["applies_to"]


def test_default_config_loads_genai_data_privacy_library():
    config = yaml.safe_load(Path("config/default.yaml").read_text(encoding="utf-8"))
    assert "owasp_genai_data_privacy" in config["payload_libraries"]


def test_payload_library_selects_genai_and_privacy_scenarios():
    library = PayloadLibrary()
    module_names = {
        "owasp_llm01_prompt_injection",
        "owasp_llm02_sensitive_information_disclosure",
        "owasp_llm03_supply_chain",
        "owasp_llm05_improper_output_handling",
        "owasp_llm06_excessive_agency",
        "owasp_llm08_vector_embedding_weaknesses",
        "owasp_llm09_misinformation",
        "owasp_llm10_unbounded_consumption",
    }
    for module_name in module_names:
        selected = library.for_module(module_name, library_names=["owasp_genai_data_privacy"])
        assert selected, module_name
        assert any((payload.metadata or {}).get("source_directory") == SOURCE_DIRECTORY for payload in selected)
