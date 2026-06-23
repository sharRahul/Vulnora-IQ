from __future__ import annotations

from pathlib import Path

import yaml

from core.payload_loader import PayloadLibrary
from modules.registry import ModuleRegistry

AI_TESTING_GUIDE_PROFILES = [
    "ai_testing_guide_foundation",
    "test_owasp_ai_testing_methodology",
    "test_owasp_genai_red_teaming_methodology",
    "test_csa_agentic_ai_red_teaming",
    "test_owasp_ai_exchange_controls",
    "test_owasp_ai_security_privacy_design",
    "test_owasp_aivss_scoring_review",
    "test_nist_ai_100_2_adversarial_ml",
]

OWASP_LAB_TARGETS = [
    "owasp_lab_agent_http",
    "owasp_lab_chat_completions",
    "owasp_lab_ollama_generate",
    "owasp_lab_webhook_json",
]


def _load_yaml(path: str) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def test_ai_testing_guide_profiles_resolve_registered_modules() -> None:
    profiles = _load_yaml("config/attack_profiles.yaml")["profiles"]
    registry = ModuleRegistry()

    for profile_name in AI_TESTING_GUIDE_PROFILES:
        assert profile_name in profiles
        assert profiles[profile_name]["modules"]
        for module_name in profiles[profile_name]["modules"]:
            assert registry.get(module_name)


def test_ai_testing_guide_payloads_are_loaded_for_framework_modules() -> None:
    payloads = PayloadLibrary().for_module("owasp_genai_red_teaming_methodology", ["ai_testing_guide"])

    assert payloads
    assert all(payload.metadata for payload in payloads)
    assert any("authorised" in payload.input_text.lower() for payload in payloads)


def test_owasp_lab_targets_are_real_local_templates_not_placeholders() -> None:
    targets = _load_yaml("config/targets.yaml")["targets"]

    for target_name in OWASP_LAB_TARGETS:
        target = targets[target_name]
        endpoint = target["endpoint"]
        assert endpoint.startswith("http://127.0.0.1")
        assert "example.invalid" not in endpoint
        assert target["auth"] == "none"
