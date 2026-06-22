from __future__ import annotations

import yaml

from scripts.refresh_mitre_atlas import refresh_mapping


def test_refresh_mapping_from_local_fixture(tmp_path) -> None:
    source = tmp_path / "ATLAS.yaml"
    existing = tmp_path / "mitre_atlas_mapping.yaml"
    output = tmp_path / "refreshed.yaml"
    source.write_text(
        yaml.safe_dump(
            {
                "version": "fixture-version",
                "matrices": [
                    {
                        "techniques": [
                            {"id": "AML.T0051", "name": "LLM Prompt Injection"},
                        ]
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    existing.write_text(
        yaml.safe_dump(
            {
                "source": {"atlas_version": "old"},
                "techniques": {"AML.T0051": {"name": "Old", "rationale": "Keep local rationale."}},
                "module_mappings": {"owasp_llm01_prompt_injection": ["AML.T0051"]},
            }
        ),
        encoding="utf-8",
    )

    refreshed = refresh_mapping(source, existing, output)
    data = yaml.safe_load(refreshed.read_text(encoding="utf-8"))

    assert data["source"]["atlas_version"] == "fixture-version"
    assert data["techniques"]["AML.T0051"]["name"] == "LLM Prompt Injection"
