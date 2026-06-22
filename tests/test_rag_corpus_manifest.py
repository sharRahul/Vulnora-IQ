from __future__ import annotations

from pathlib import Path

from core.scanner import Scanner
from rag_testing.corpus_manifest import CorpusManifestValidator


def test_demo_rag_manifest_validates() -> None:
    result = CorpusManifestValidator().validate(Path("config/rag_corpus_manifest.yaml"))

    assert result.status == "pass"
    assert result.document_count == 2
    assert not result.errors


def test_rag_profile_policy_uses_manifest() -> None:
    result = Scanner().scan(target_name="demo", profile_name="rag")

    rag_policy = next(policy for policy in result.policy_results if policy.policy_id == "rag_corpus_integrity_required")
    assert rag_policy.status == "pass"
    assert rag_policy.evidence["document_count"] == 2
