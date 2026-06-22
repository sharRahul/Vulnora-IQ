from __future__ import annotations

from rag_testing.retrieval_harness import LocalRetrievalHarness


def test_local_rag_retrieval_harness_passes_demo_scenarios() -> None:
    result = LocalRetrievalHarness().run()

    assert result.status == "pass"
    assert result.scenario_count == 3
    assert result.failed_count == 0
    assert all(item.source_trust_score >= result.minimum_source_trust_score for item in result.results)


def test_rag_access_boundary_blocks_external_group() -> None:
    result = LocalRetrievalHarness().run()

    external = next(item for item in result.results if item.scenario_id == "rag-query-003")
    assert external.status == "pass"
    assert external.retrieved_documents == []
