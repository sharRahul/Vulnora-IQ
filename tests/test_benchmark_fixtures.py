from __future__ import annotations

from benchmarks.fixture_validation import BenchmarkFixtureValidator


def test_owasp_starter_fixture_covers_all_categories() -> None:
    result = BenchmarkFixtureValidator().validate()

    assert result.status == "pass"
    assert result.fixture_count == 10
    assert len([module for module in result.covered_modules if module.startswith("owasp_llm")]) == 10
